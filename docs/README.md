# Mkdocs Helm Plugin
An Mkdocs Plugin to turn github pages as an helm repo.

# How to use
1. Adding helm-repo plugin into mkdocs.yaml and configure it.
   ```yaml
   plugins:
    - helm-repo:
        chart: alb-ingress-controller-helm
   ```
1. Supported plugin configurations:
    - chart: Required, path to your helm chart from root directory.
    - chart_dir: Optional(default to 'charts'), http path to host your actual charts
    - helm_repo_url: Optional(default to github pages), intended helm repository url
1. Supported environment variables:
    - HELM_BIN: Optional(default to 'helm') path to your helm binary
    - GIT_BIN: Optional(default to 'git') path to your git binary