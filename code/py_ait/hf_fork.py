import click
import json
from huggingface_hub import create_repo
import os,threading

pool_sema = None

def print_yellow(msg):
    print(f'\033[33m{msg}\033[0m')

def print_green(msg):
    print(f'\033[32m{msg}\033[0m')

def init_env(hf_username,hf_token):
    # run bash command to init env
    bash_script = f"""
    #!/bin/bash
    mkdir -p .tmp
    apt update
    # install git-lfs
    apt-get install git git-lfs -y
    # add git-credential
    git config --global credential.helper store --replace-all
    git config --global lfs.allowincompletepush true

    echo "https://{hf_username}:{hf_token}@huggingface.co" > ~/.git-credentials
    """
    return os.system(bash_script)

def create_hf_repo(source_repo,target_repo,repo_type,seperator="__"):
    # create huggingface repo if not exist
    if target_repo is None:
        target_repo = f"{os.environ['HF_USERNAME']}/{source_repo.replace('/',seperator)}"
    create_repo(target_repo, repo_type=repo_type,token=os.environ['HF_TOKEN'],exist_ok=True,private=True)
    return target_repo

def multi_thread_fork(source_repo_id,target_repo_id,repo_type,seperator="__",retry_count=10):
    with pool_sema:
        fork(source_repo_id,target_repo_id,repo_type,seperator,retry_count)

def fork(source_repo_id,target_repo_id,repo_type,seperator="__",retry_count=10):
    # generate random path
    random_folder_name = os.urandom(16).hex()
    clone_folder = f'/tmp/ai-toolbox/hf-fork/{random_folder_name}'
    def retry():
        os.system('rm -rf {clone_folder}')
        if retry_count > 0:
            print_yellow(f'fork failure,will retry! left {retry_count} retry count')
            fork(source_repo_id,target_repo_id,repo_type,retry_count=retry_count-1)
        else:
            print_yellow(f'fork {source_repo_id} to {target_repo_id} failure!')
            print_yellow('stop retry!')
    try:
        target_repo_id=create_hf_repo(source_repo_id,target_repo_id,repo_type,seperator)
        if repo_type == "dataset":
            url_repo_type = "datasets"
        if repo_type == "model":
            url_repo_type = "models"
        sourceRepo=f"https://huggingface.co/{url_repo_type}/{source_repo_id}"
        targetRepo=f"https://huggingface.co/{url_repo_type}/{target_repo_id}"
        os.system(f'rm -rf {clone_folder}')
        os.system(f'mkdir -p {clone_folder}')
        print_green(f'fork {source_repo_id} to {target_repo_id} start!')
        bash_script = f"""
        #!/bin/bash
        sourceRepo={sourceRepo}
        targetRepo={targetRepo}
        tmp_repo_folder={clone_folder}
        git clone $sourceRepo $tmp_repo_folder
        huggingface-cli lfs-enable-largefiles $tmp_repo_folder
        cd $tmp_repo_folder
        git fetch --all
        git lfs fetch --all
        git remote add target-origin $targetRepo
        git push target-origin --all --force --progress
        rm -rf $tmp_repo_folder
        """
        result = os.system(bash_script)
        os.system('rm -rf {clone_folder}')
        if result != 0:
            retry()
        else:
            print_green(f'fork {source_repo_id} to {target_repo_id} success!')
    except Exception as e:
        print_yellow(f'An error occurred: {e}')
        retry()

@click.command()
@click.option('--hf_username', help='your hugging face username.', required=True)
@click.option('--hf_token', help='your hugging face token.',required=True)
@click.option('--repo_info_path', help='repo info file for fork multi repos at once, demo please read README.md',required=False)
@click.option('--retry_count', help='retry count after a failure, default 10', default=10, required=False)
@click.option('--source_repo', help='source repo name which you want to fork, like $your_username/$repo_name', required=False)
@click.option('--target_repo', help='target repo name which fork to, like $your_username/$repo_name. if not pass,use your_hf_username/source_repo.replace_/_with_separator', required=False)
@click.option('--repo_type', help='required when you pass args without repo_info_path, model or dataset',type=click.Choice(['dataset','model']),default="dataset", required=False)
@click.option('--separator', help='a string used to replace / when you did not pass target_repo without --repo_info_path',default='__', required=False)
@click.option('--thread_nums', help='the number of threads concurrently executing the target, default 5', default=5, required=False)
@click.option('--disable-multi-task', help='disable multi task for forking multi repos when you pass, only work with --repo_info_path',default=False, required=False,is_flag=True)
def run(hf_username,hf_token,repo_info_path,retry_count=10,source_repo=None,target_repo=None,repo_type=None,separator='__',disable_multi_task=False,thread_nums=5):
    os.environ['HF_USERNAME'] = hf_username
    os.environ['HF_TOKEN'] = hf_token
    init_env(hf_username,hf_token)
    """
    fork model and dataset from hugging face hub,
    fork_repo_info file is json format, look like:
    {
        "model":[
            {
                "source":"OpenAssistant/falcon-40b-megacode2-oasst",
                "target":"your_name/your_repo"
            }        
        ],
        "dataset":[
            {
                "source":"PygmalionAI/PIPPA",
                "target":"your_name/your_repo"
            }
        ]
    }
    """
    # load repo info from json
    if repo_info_path:
        with open(repo_info_path) as f:
            repo_info = json.load(f)
            try:
                threads = []
                def thread_fork(repos,repo_type):
                    for repo in repos:
                        source_repo_id = repo["source"]
                        target_repo_id = None
                        if "target" in repo:
                            target_repo_id = repo["target"]
                        if disable_multi_task:
                            fork(source_repo_id,target_repo_id,repo_type,retry_count=retry_count,seperator=separator)
                        else:
                            global pool_sema
                            pool_sema=threading.BoundedSemaphore(value=thread_nums)
                            thread = threading.Thread(target=multi_thread_fork,
                                                    kwargs={
                                                        "source_repo_id":source_repo_id,
                                                        "target_repo_id":target_repo_id,
                                                        "repo_type":repo_type,
                                                        "retry_count":retry_count,
                                                        "seperator":separator
                                                        })
                            thread.start()
                            threads.append(thread)
                # fork model
                if "model" in repo_info:
                    thread_fork(repo_info["model"],"model")
                # fork dataset
                if "dataset" in repo_info:
                    thread_fork(repo_info["dataset"],"dataset")
                for thread in threads:
                    thread.join()
            except Exception as e:
                raise e
    else:
        if source_repo and repo_type:
            fork(source_repo,target_repo,repo_type,retry_count=retry_count,seperator=separator)
        else:
            print_yellow("you must pass args without repo_info_path, please read readme.md")

# if __name__ == '__main__':
#     run()
