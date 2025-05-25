from huggingface_hub import upload_folder, HfApi
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    logging.info("Starting update of bart-finetuned to Hugging Face")
    # Delete existing files to avoid conflicts (optional, for full overwrite)
    api = HfApi()
    existing_files = api.list_repo_files(repo_id="levii831/linebottest-model", repo_type="model")
    for file in existing_files:
        api.delete_file(
            path_in_repo=file,
            repo_id="levii831/linebottest-model",
            repo_type="model",
            commit_message=f"Remove {file} before updating model"
        )
    # Upload new model
    upload_folder(
        folder_path="C:/Users/user/Documents/python_projects/linebottest/bart-finetuned",
        repo_id="levii831/linebottest-model",
        repo_type="model",
        commit_message="Update fine-tuned BART model with new weights"
    )
    logging.info("Model update complete!")
except Exception as e:
    logging.error(f"Model update failed: {e}")
    raise