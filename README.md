# Unified Quantinuum documentation

This repository contains landing pages and deployment workflows
for a unified Quantinuum documentation site.

Rather than hosting the docs for our software and hardware
products in multiple different places, we'd like to put them in
one shared website.

However, because we have a lot of different software products
with different dependencies, we'd like to rely on the product
repositories themselves to build the docs (using a shared Sphinx
theme). The code in this repo takes the HTML that those projects
build, and puts them together into one site.

## Setting up this repo, or a copy of it

[Set up Github Pages on this repo so that it can take a Github Actions workflow as a source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#publishing-with-a-custom-github-actions-workflow).

For the official unified documentation site, you'll also need to [set up a custom domain](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages).

## Setting up other products' documentation to import it here

Set up the product's documentation workflow so that on every
 tagged release of the product, it:
  * generates the documentation with a custom `conf.py` file that
    matches the theme of the shared docs site
  * makes a `.tar.gz` file of the generated documentation
  * upload the `.tar.gz` file as an asset to the tagged release.

Set up appropriate access token(s) so that this repository can
access the release assets of the product's repo.
