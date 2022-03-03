# A Tool for quick review GitHub issues (including their comments)
# User can then choose to block the user or not

import requests
import json
import os
import sys
import argparse

WHITELIST_FILENAME = 'whitelist.txt'
whitelist = []


def save_whitelist():
    # write the white list to a file
    with open(WHITELIST_FILENAME, 'w') as f:
        for user in whitelist:
            f.write(user + '\n')


def load_whitelist():
    # load the white list from a file
    if os.path.isfile(WHITELIST_FILENAME):
        with open(WHITELIST_FILENAME, 'r') as f:
            for line in f:
                if line.strip():
                    whitelist.append(line.strip())


class GithubClient:
    BASE_URL = 'https://api.github.com/'

    def __init__(self, username, token):
        # use OAuth tokens to authenticate to the GitHub API
        self.username = username
        self.token = token
        self.session = requests.Session()
        self.session.auth = (username, token)
        self.session.headers.update(
            {'Accept': 'application/vnd.github.v3+json'})

    def get_blocklist(self):
        # get the list of blocked users
        response = self.session.get(self.BASE_URL + 'user/blocks')
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def block_user(self, username):
        # block a user
        response = self.session.put(
            self.BASE_URL + 'user/blocks/' + username)
        if response.status_code == 204:
            return True
        else:
            return False

    def is_blocked(self, username):
        # check if a user is blocked
        response = self.session.get(
            self.BASE_URL + 'user/blocks/' + username)
        if response.status_code == 204:
            return True
        else:
            return False

    def get_repo_issues(self, owner, repo, since = None, page=1):
        # get the list of issues for a repo
        response = self.session.get(
            self.BASE_URL + 'repos/' + owner + '/' + repo + '/issues',
            params={'page': page, 'per_page': 100, 'since': since})
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_issue_comments(self, owner, repo, issue_number):
        # get the list of comments for an issue
        response = self.session.get(
            self.BASE_URL + 'repos/' + owner + '/' + repo + '/issues/' +
            str(issue_number) + '/comments')
        if response.status_code == 200:
            return response.json()
        else:
            return None


def print_separator():
    # print a separator
    print('-' * 80)


def ask_block(user, client):
    # ask user whether to block a user
    if user['login'] in whitelist:
        print('\033[93mUser %s is in the whitelist\033[0m' % user['login'])
    elif client.is_blocked(user['login']):
        print('\033[93mUser %s is already blocked\033[0m' % user['login'])
    else:
        print("\033[91mBlock user `%s'?\033[0m" % user['login'])
        while True:
            answer = input('y/n/w/q: ')
            if answer == 'y':
                if client.block_user(user['login']):
                    print('Blocked user %s' % user['login'])
                else:
                    print('Could not block user %s' % user['login'])
                break
            elif answer == 'n':
                print('Not blocking user %s' % user['login'])
                break
            elif answer == 'w':
                whitelist.append(user['login'])
                print('Added %s to whitelist' % user['login'])
                save_whitelist()
                break
            elif answer == 'q':
                print('Quitting')
                sys.exit(0)
            else:
                print('Please answer y/n/q')


def process_single_issue(issue, client, repo_owner, repo_name):
    # Show issue content and ask user whether to block the user.
    # if there are comments, show them too.
    print('Issue #' + str(issue['number']) + ': ' + issue['title'])
    print('User: ' + issue['user']['login'])
    if issue['body']:
        print('Content: \n' + issue['body'])
        print_separator()
        ask_block(issue['user'], client)

    # show comments
    if issue['comments'] > 0:
        print('\nComments:')
        comments = client.get_issue_comments(repo_owner, repo_name, issue['number'])
        if comments:
            for comment in comments:
                print('\nComment by ' + comment['user']['login'] + ':')
                print(comment['body'])
                ask_block(comment['user'], client)
                print_separator()
        else:
            print('Could not get comments')

    print_separator()


def main():
    p = argparse.ArgumentParser(description="GitHub Quick Blocker")
    p.add_argument('-u', '--username', help='GitHub username')
    p.add_argument('-t', '--token', help='GitHub OAuth token')
    p.add_argument('-r', '--repo', help='GitHub repository URL (e.g. https://github.com/facebook/react)')
    try:
        args = vars(p.parse_args())
    except Exception as e:
        print(e)
        sys.exit()

    if args['username'] is None or args['token'] is None:
        print('Please provide a username and OAuth token')
        sys.exit()

    if args['repo'] is None:
        print('Please provide a repository URL')
        sys.exit()

    repo_owner = args['repo'].split('/')[-2]
    repo_name = args['repo'].split('/')[-1]

    print('\033[92mGitHub Quick Blocker\033[0m')
    print('Repository: ' + repo_owner + '/' + repo_name)
    print('Logged in as: ' + args['username'])
    print_separator()

    client = GithubClient(args['username'], args['token'])

    issues = client.get_repo_issues(repo_owner, repo_name)
    if issues is None:
        print('Could not get issues')
        sys.exit()

    page = 1
    while issues:
        for issue in issues:
            try:
                process_single_issue(issue, client, repo_owner, repo_name)
            except Exception as e:
                print(e)
                print('Could not process issue #' + str(issue['number']))
        page += 1
        issues = client.get_repo_issues(repo_owner, repo_name, page)


if __name__ == '__main__':
    main()