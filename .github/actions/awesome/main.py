import os
from typing import List, Optional

import yaml
from github import Github
from jinja2 import Template
from pydantic import BaseModel, BaseSettings, HttpUrl


class Settings(BaseSettings):
    template_path: str
    output_path: str
    data_path: str

settings = Settings()
g = Github(os.getenv("GITHUB_TOKEN"))


class Repository(BaseModel):
    name: str
    repo: HttpUrl
    description: str
    stars: Optional[int]


class RepositoriesData(BaseModel):
    repositories: List[Repository]


def read_awesome() -> RepositoriesData:
    with open(settings.data_path, "r") as file:
        repos = RepositoriesData(**yaml.safe_load(file))
    return repos


def render_readme(data: RepositoriesData) -> str:
    with open(settings.template_path, "r") as readme_template:
        template = Template(readme_template.read())
    return template.render(**data.dict())


def write_readme(text: str) -> None:
    with open(settings.output_path, "w") as readme_file:
        readme_file.write(text)


def load_stars(data: RepositoriesData):
    for repository in data.repositories:
        repo = g.get_repo(repository.repo.path.strip("/"))
        repository.stars = repo.stargazers_count


if __name__ == "__main__":
    data = read_awesome()
    load_stars(data)
    data.repositories = sorted(data.repositories, key=lambda x: -x.stars)
    text_readme = render_readme(data)
    write_readme(text_readme)
