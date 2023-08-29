import click
import json
from huggingface_hub import snapshot_download
from datasets import load_dataset,DownloadConfig
import threading

@click.command()
@click.option('--repo_info_path', help='hugging face repo info, demo please read readme.md',required=True)
@click.option('--retry_count', help='retry count after a failure,default 10', default=10, required=False)
@click.option('--thread_nums', help='the number of threads concurrently executing the target, default 5', default=5, required=False)
def run(repo_info_path,retry_count=10,thread_nums=5):
    """
    download model and dataset from hugging face hub, the content will download to huggingface default .cache dir, like ~/.cache/huggingface
    repo_info file is json format, look like:
    {
        "model":[
            "OpenAssistant/falcon-40b-megacode2-oasst",
            "stabilityai/stable-diffusion-xl-base-1.0"
        ],
        "dataset":[
            "OpenAssistant/oasst1",
            "PygmalionAI/PIPPA"
        ]
    }
    """
    pool_sema=threading.BoundedSemaphore(value=thread_nums)
    def download(repo_id,repo_type):
        with pool_sema:
            for i in range(int(retry_count)):
                try:
                    # dataset downloaded via snapshot_download cannot be load automatically via load_dataset, wo we use load_dataset to download dataset
                    if repo_type == "dataset":
                        download_config = DownloadConfig(max_retries=100)
                        load_dataset(repo_id,download_config=download_config)
                    else:
                        snapshot_download(repo_id=repo_id, repo_type=repo_type,resume_download=True)
                    break
                except Exception as e:
                    print(f'An error occurred: {e}')
                    print(f'retry {i+1} times')
                    if i == int(retry_count)-1:
                        print(f'failed to download {repo_id}')
                        break
    # load repo info from json
    with open(repo_info_path) as f:
        repo_info = json.load(f)
        try:
            threads = []
            # download model
            if "model" in repo_info:
                for model in repo_info["model"]:
                    thread = threading.Thread(target=download,kwargs={"repo_id":model,"repo_type":"model"})
                    thread.start()
                    threads.append(thread)
            # download dataset
            if "dataset" in repo_info:
                for dataset in repo_info["dataset"]:
                    thread = threading.Thread(target=download,kwargs={"repo_id":dataset,"repo_type":"dataset"})
                    thread.start()
                    threads.append(thread)
            for thread in threads:
                thread.join()
        except Exception as e:
            print(f'An error occurred: {e}')


if __name__ == '__main__':
    run()
