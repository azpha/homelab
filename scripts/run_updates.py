import requests
import subprocess
import os
import yaml

DISCORD_WEBHOOK_URL = os.environ.get("UPDATES_DISCORD_WEBHOOK")

def normalize_image_name(image_name):
  # strip the tag (but not a registry port) and docker hub prefixes
  name, _, tag = image_name.rpartition(":")
  if name and "/" not in tag:
    image_name = name
  for prefix in ("docker.io/", "library/"):
    if image_name.startswith(prefix):
      image_name = image_name[len(prefix):]
  return image_name

def search_for_images(image_name):
  tasks_folder = os.path.realpath(os.path.join('./', 'tasks'))
  image_name = normalize_image_name(image_name)
  matches = []

  for category in sorted(os.listdir(tasks_folder)):
    tasks = sorted(os.listdir(os.path.join(tasks_folder, category)))
    for task in tasks:
      with open(os.path.join(tasks_folder, category, task), 'r') as file:
        data = yaml.safe_load(file) or []

        for key in data:
          image = key.get("vars", {}).get("image")
          if not image:
            continue
          if normalize_image_name(image["name"]) == image_name:
            matches.append(f"{task.split(".")[0]}_deploy")
            break

  return matches

def main():
  update_list = requests.get("https://cup.fntz.net/api/v3/json")
  update_list.raise_for_status()
  update_list = update_list.json()
  refs = []
  deployable_tags = []

  for image in update_list["images"]:
    reference = image["reference"]
    result = image["result"]

    # don't attempt to update if unable
    if not image["in_use"]:
      continue
    if not result or not result["has_update"]:
      continue
    # version updates need a tag bump in the repo, redeploying won't pick them up
    if (result.get("info") or {}).get("type") != "digest":
      continue

    refs.append(reference)

  print("attempting to match images to references: " + ", ".join(refs))
  for reference in refs:
    tags = search_for_images(reference)
    for tag in tags:
      if tag not in deployable_tags:
        deployable_tags.append(tag)
    if not tags:
      print("Could not find suitable container for " + reference)
  
  if len(deployable_tags) > 0:
    print(f"Found {len(deployable_tags)}, deploying..")
    tag_string = ",".join(deployable_tags)
    subprocess.run(f'ANSIBLE_CONFIG=ansible.cfg ansible-playbook main.yml --tags {tag_string} -l bear --vault-password-file=~/.vault_pass.txt', shell=True, check=True)

    print("Attempting to clean up dangling/unassumed images")
    subprocess.run('ANSIBLE_CONFIG=ansible.cfg ansible bear -m command -a "docker image prune -af"', shell=True)

    print("Redeployed all images, refreshing Cup")
    requests.get("https://cup.fntz.net/api/v3/refresh")

    if DISCORD_WEBHOOK_URL:
      print("sending discord notification..")
      body = {
        "username": "Homelab Updates",
        "embeds": [
          {
            "title": "Updated containers automatically!",
            "description": f"Automatically redeployed containers recognized to need updates via Cup\n```{", ".join(deployable_tags)}```"
          }
        ]
      }
      headers = {
        "content-type": "application/json"
      }
      requests.post(DISCORD_WEBHOOK_URL, json=body, headers=headers)
  else:
    print("All up to date! :)")

if __name__ == "__main__":
  main()
