import logging
import requests
import os
from plugin.plugin_interface import AbstractPlugin, PluginResult
from jarvis.jarvis import takecommand

class GithubPlugin(AbstractPlugin):
    def __init__(self):
        # 从环境变量中获取 GitHub 令牌
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN 环境变量未设置")
        self.logger = None
        self.username = self.get_username()

    def valid(self) -> bool:
        # 验证 GitHub 令牌是否有效
        headers = {"Authorization": f"token {self.token}"}
        response = requests.get("https://api.github.com/user", headers=headers)
        return response.status_code == 200

    def init(self, logger: logging.Logger):
        self.logger = logger
        self.logger.info("GithubPlugin 已初始化")

    def get_name(self):
        return "GithubPlugin"

    def get_chinese_name(self):
        return "GitHub插件"

    def get_description(self):
        return "该插件与 GitHub 交互，以执行项目搜索、创建、更新等操作。"

    def get_parameters(self):
        return {
            "operation": "要执行的操作 (search, create, update, delete, list_repos, get_repo, create_issue, list_issues, create_pr, list_prs)",
            "search_query": "GitHub 仓库搜索查询",
            "repo_name": "用于创建、更新、删除、获取仓库、创建 issue、列出 issues、创建 PR 和列出 PR 的仓库名称",
            "repo_description": "用于创建或更新操作的仓库描述",
            "private": "布尔值，表示仓库是否为私有",
            "issue_title": "用于创建 issue 操作的 issue 标题",
            "issue_body": "用于创建 issue 操作的 issue 内容",
            "pr_title": "用于创建 PR 操作的 PR 标题",
            "pr_body": "用于创建 PR 操作的 PR 内容",
            "base_branch": "用于创建 PR 操作的基准分支",
            "head_branch": "用于创建 PR 操作的头部分支"
        }

    def run(self, takecommand: str, args: dict) -> PluginResult:
        operation = args.get("operation")
        if operation == "search":
            return self.search_repositories(args.get("search_query"))
        elif operation == "create":
            return self.create_repository(args.get("repo_name"), args.get("repo_description"), args.get("private"))
        elif operation == "update":
            return self.update_repository(args.get("repo_name"), args.get("repo_description"))
        elif operation == "delete":
            return self.delete_repository(args.get("repo_name"))
        elif operation == "list_repos":
            return self.list_repositories()
        elif operation == "get_repo":
            return self.get_repository(args.get("repo_name"))
        elif operation == "create_issue":
            return self.create_issue(args.get("repo_name"), args.get("issue_title"), args.get("issue_body"))
        elif operation == "list_issues":
            return self.list_issues(args.get("repo_name"))
        elif operation == "create_pr":
            return self.create_pull_request(args.get("repo_name"), args.get("pr_title"), args.get("pr_body"), args.get("base_branch"), args.get("head_branch"))
        elif operation == "list_prs":
            return self.list_pull_requests(args.get("repo_name"))
        else:
            return PluginResult.new("无效操作", False)

    def search_repositories(self, query):
        headers = {"Authorization": f"token {self.token}"}
        params = {"q": query}
        response = requests.get("https://api.github.com/search/repositories", headers=headers, params=params)
        if response.status_code == 200:
            return PluginResult.new(response.json(), False)
        else:
            return PluginResult.new(f"搜索仓库失败: {response.status_code}", False)

    def create_repository(self, name, description, private):
        headers = {"Authorization": f"token {self.token}"}
        data = {
            "name": name,
            "description": description,
            "private": private
        }
        response = requests.post("https://api.github.com/user/repos", headers=headers, json=data)
        if response.status_code == 201:
            return PluginResult.new("仓库创建成功", False)
        else:
            return PluginResult.new(f"创建仓库失败: {response.status_code}", False)

    def update_repository(self, name, description):
        headers = {"Authorization": f"token {self.token}"}
        data = {
            "name": name,
            "description": description
        }
        response = requests.patch(f"https://api.github.com/repos/{self.username}/{name}", headers=headers, json=data)
        if response.status_code == 200:
            return PluginResult.new("仓库更新成功", False)
        else:
            return PluginResult.new(f"更新仓库失败: {response.status_code}", False)

    def delete_repository(self, name):
        headers = {"Authorization": f"token {self.token}"}
        response = requests.delete(f"https://api.github.com/repos/{self.username}/{name}", headers=headers)
        if response.status_code == 204:
            return PluginResult.new("仓库删除成功", False)
        else:
            return PluginResult.new(f"删除仓库失败: {response.status_code}", False)

    def list_repositories(self):
        headers = {"Authorization": f"token {self.token}"}
        response = requests.get(f"https://api.github.com/user/repos", headers=headers)
        if response.status_code == 200:
            return PluginResult.new(response.json(), False)
        else:
            return PluginResult.new(f"列出仓库失败: {response.status_code}", False)

    def get_repository(self, name):
        headers = {"Authorization": f"token {self.token}"}
        response = requests.get(f"https://api.github.com/repos/{self.username}/{name}", headers=headers)
        if response.status_code == 200:
            return PluginResult.new(response.json(), False)
        else:
            return PluginResult.new(f"获取仓库失败: {response.status_code}", False)

    def create_issue(self, repo_name, title, body):
        headers = {"Authorization": f"token {self.token}"}
        data = {
            "title": title,
            "body": body
        }
        response = requests.post(f"https://api.github.com/repos/{self.username}/{repo_name}/issues", headers=headers, json=data)
        if response.status_code == 201:
            return PluginResult.new("Issue 创建成功", False)
        else:
            return PluginResult.new(f"创建 Issue 失败: {response.status_code}", False)

    def list_issues(self, repo_name):
        headers = {"Authorization": f"token {self.token}"}
        response = requests.get(f"https://api.github.com/repos/{self.username}/{repo_name}/issues", headers=headers)
        if response.status_code == 200:
            return PluginResult.new(response.json(), False)
        else:
            return PluginResult.new(f"列出 Issues 失败: {response.status_code}", False)

    def create_pull_request(self, repo_name, title, body, base_branch, head_branch):
        headers = {"Authorization": f"token {self.token}"}
        data = {
            "title": title,
            "body": body,
            "head": head_branch,
            "base": base_branch
        }
        response = requests.post(f"https://api.github.com/repos/{self.username}/{repo_name}/pulls", headers=headers, json=data)
        if response.status_code == 201:
            return PluginResult.new("Pull Request 创建成功", False)
        else:
            return PluginResult.new(f"创建 Pull Request 失败: {response.status_code}", False)

    def list_pull_requests(self, repo_name):
        headers = {"Authorization": f"token {self.token}"}
        response = requests.get(f"https://api.github.com/repos/{self.username}/{repo_name}/pulls", headers=headers)
        if response.status_code == 200:
            return PluginResult.new(response.json(), False)
        else:
            return PluginResult.new(f"列出 Pull Requests 失败: {response.status_code}", False)

    def get_username(self):
        headers = {"Authorization": f"token {self.token}"}
        response = requests.get("https://api.github.com/user", headers=headers)
        if response.status_code == 200:
            return response.json()["login"]
        else:
            raise Exception("获取用户名失败")
