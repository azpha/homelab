import requests
import subprocess
import os
import yaml

DISCORD_WEBHOOK_URL = os.environ.get("UPDATES_DISCORD_WEBHOOK")

def search_for_image(image_name):
  tasks_folder = os.path.realpath(os.path.join('./', 'tasks'))
  if "library/" in image_name:
    image_name = image_name.replace("library/", "")
  image_name = image_name.split(":")[0]

  for task in os.listdir(tasks_folder):
    with open(os.path.join(tasks_folder, task), 'r') as file:
      data = yaml.safe_load(file)

      for key in data:
        if "vars" in key:
          if image_name in key["vars"]["image"]["name"] or image_name == key["vars"]["image"]["name"]:
            return f"{task.split(".")[0]}_deploy"

def main():
  update_list = requests.get("https://cup.fntz.net/api/v3/json")
  update_list.raise_for_status()
  update_list = update_list.json()
  refs = []
  deployable_tags = []

  for image in update_list["images"]:
    reference = image["reference"]

    # don't attempt to update if unable
    if not image["in_use"]:
      continue
    if ":latest" not in reference:
      continue
    if image["result"] and not image["result"]["has_update"]:
      continue

    refs.append(reference)

  print("attempting to match images to references: " + ", ".join(refs))
  for reference in refs:
    tag = search_for_image(reference)
    if tag:
      deployable_tags.append(tag)
    else:
      print("Could not find suitable container for " + reference)
  
  if len(deployable_tags) > 0:
    print(f"Found {len(deployable_tags)}, deploying..")
    for ansible_tag in deployable_tags:
      subprocess.run(f'ANSIBLE_CONFIG=ansible.cfg ansible-playbook main.yml --tags {ansible_tag} -l bear --vault-password-file=~/.vault_pass.txt', shell=True)

    print("Redeployed all images, refreshing Cup")
    requests.get("https://cup.fntz.net/api/v3/refresh")

    print("Attempting to clean up dangling/unassumed images")
    subprocess.run(f"docker image prune -a -f", shell=True)

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
