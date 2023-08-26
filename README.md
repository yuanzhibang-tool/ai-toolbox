# AI-Toolbox

## Command

---

### ait-download

>Download hf model,dataset and will retry after a failure, default 10 times.

```bash
ait-download \
--repo_info_path=/your_repo_info.json \
--retry_count=2 \
--thread_nums=5
```

#### Args description

|name|description|required|default|
|---|---|---|---|
|`--repo_info_path`|repo info file for download multi repos at once, demo below!|`True`|`None`|
|`--retry_count`|retry count after a failure|`False`|`10`|
|`--thread_nums`|the number of threads concurrently executing the target|`False`|`5`|

#### Demo repo_info.json

```json
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
```



---

### ait-fork

>fork hf model, dataset and will retry after a failure, default 10 times.

```bash
# fork with fork_repo_info.json
ait-fork \
--repo_info_path=/your_repo_info.json \
--retry_count=2 \
--hf_username=your_hf_username \
--hf_token=your_hf_token \
--separator=__ \
--thread_nums=5

# fork without fork_repo_info.json
ait-fork \
--retry_count=2 \
--hf_username=your_hf_username \
--hf_token=your_hf_token \
--separator=__ \
--source_repo=source_repo \
--target_repo=your_target_repo \
--repo_type=dataset|model \
--disable-multi-task
```

#### Args description

>you must pass `--repo_info_path` or `--source_repo` at least one!

|name|description|required|default|
|---|---|---|---|
|`--hf_username`|your hugging face username|`True`|`None`|
|`--hf_token`|your hugging face token|`True`|`None`|
|`--repo_info_path`|repo info file for fork multi repos at once, demo below!|`False`|`None`|
|`--retry_count`|retry count after a failure|`False`|`10`|
|`--separator`|a string used to replace `/` when you did not pass `target_repo` without `--repo_info_path`|`False`|`__`|
|`--source_repo`|the source repo you want to fork! eg: `PygmalionAI/PIPPA`,|`False`|`10`|
|`--target_repo`|the target repo you want to fork to! eg: `your_hf_username/your_repo_name`, if not pass, use `your_hf_username/source_repo.replace_/_with_separator`|`False`|`None`|
|`--repo_type`|`model` or `dataset`|`False`|`dataset`|
|`--disable-multi-task`|disable multi task for forking multi repos when you pass, only work with `--repo_info_path`|`False`|`False`|
|`--thread_nums`|the number of threads concurrently executing the target|`False`|`5`|
#### Demo fork_repo_info.json

```json
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
```