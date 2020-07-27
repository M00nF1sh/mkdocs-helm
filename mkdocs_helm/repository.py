import mkdocs
import subprocess
import pathlib
import os
import logging

logger = logging.getLogger(__name__)


class HelmRepositoryPlugin(mkdocs.plugins.BasePlugin):
    config_scheme = (
        ('chart', mkdocs.config.config_options.Type(
            str, required=True)),
        ('chart_dir', mkdocs.config.config_options.Type(
            str, default='charts')),
        ('helm_repo_url', mkdocs.config.config_options.Type(
            str, default='')),  # If unspecified, repo-url will be detected as github pages.
    )

    def on_post_build(self, config):
        git_bin = os.getenv('GIT_BIN', 'git')
        helm_bin = os.getenv('HELM_BIN', 'helm')

        remote_name = config['remote_name']
        remote_branch = config['remote_branch']
        site_dir = config['site_dir']

        chart_dir = self.config['chart_dir']
        helm_repo_url = self.config['helm_repo_url']
        if not helm_repo_url:
            helm_repo_url = self.get_github_pages_url(git_bin, remote_name)
        chart = self.config['chart']

        self.build_chart_dir(
            git_bin, remote_name, remote_branch, site_dir, chart_dir)
        self.build_chart(helm_bin, site_dir, chart_dir, chart)
        self.build_chart_index(helm_bin, site_dir, helm_repo_url)

    def build_chart_dir(self, git_bin, remote_name, remote_branch, site_dir, chart_dir):
        original_charts_exists = self.is_original_charts_exists(
            git_bin, remote_name, remote_branch, chart_dir)
        if original_charts_exists:
            self.checkout_original_charts(
                git_bin, remote_name, remote_branch, site_dir, chart_dir)
        else:
            logger.warning(
                'no charts detected in {}/{}'.format(remote_name, remote_branch))
            output_chart_dir = pathlib.Path(site_dir) / pathlib.Path(chart_dir)
            output_chart_dir.mkdir()

    def build_chart(self, helm_bin, site_dir, chart_dir, chart):
        output_chart_dir = (pathlib.PurePath(site_dir) /
                            pathlib.PurePath(chart_dir)).as_posix()
        command = [helm_bin, 'package', '-d', output_chart_dir, chart]

        # Pass the git ref in GitHub Actions
        git_ref = os.getenv('GITHUB_REF')
        if git_ref is not None and git_ref.startswith('refs/tags/') and os.getenv('HELM_USE_GIT_TAG') is not None:
            version = git_ref[10:]
            command += ['--version', version, '--app-version', version]
            print("Overwriting helm chart version and app-version with git tag '" + version + "'")

        subprocess.check_output(command)

    def build_chart_index(self, helm_bin, site_dir, helm_repo_url):
        command = [helm_bin, 'repo', 'index', site_dir, '--url', helm_repo_url]
        subprocess.check_output(command)

    def is_original_charts_exists(self, git_bin, remote_name, remote_branch, chart_dir):
        command = [git_bin, 'ls-tree', '-d',
                   '{}/{}:{}'.format(remote_name, remote_branch, chart_dir)]
        try:
            subprocess.check_call(command)
            return True
        except subprocess.CalledProcessError:
            return False

    def checkout_original_charts(self, git_bin, remote_name, remote_branch, site_dir, chart_dir):
        command = [git_bin, '--work-tree={}'.format(site_dir), 'checkout', "{}/{}".format(
            remote_name, remote_branch), "--", chart_dir]
        subprocess.check_output(command)

    def get_github_pages_url(self, git_bin, remote_name):
        command = [git_bin, 'config', '--get',
                   'remote.{}.url'.format(remote_name)]
        url = subprocess.check_output(command).decode('utf-8').strip()
        path = None
        if 'github.com/' in url:
            _, path = url.split('github.com/', 1)
        elif 'github.com:' in url:
            _, path = url.split('github.com:', 1)
        username, repo = path.split('/', 1)
        if repo.endswith('.git'):
            repo = repo[:-len('.git')]
        return 'https://{}.github.io/{}'.format(username, repo)
