import requests
import subprocess
import os
import yaml

def search_for_image(image_name):
  tasks_folder = os.path.realpath(os.path.join('./', 'tasks'))
  if "library/" in image_name:
    image_name = image_name.replace("library/", "")
  
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

  deployable_tags = []
  with open("main.yml", 'r') as file:
    data = yaml.safe_load(file)
    for host in data:
      if "tasks" in host:
        for task in host['tasks']:
          deployable_tags.append(task['tags'])

  if len(update_list["images"]) > 0:
    already_deployed = []
    actually_updatable = []
    blacklist = []

    for image in update_list["images"]:
      if image['result']['has_update']:
        if image in blacklist:
          print(f"[UPDATE] Ignoring '{image}' due to its blacklist")
        elif 'version_update_type' in image['result']['info'] and image['result']['info']['version_update_type'] != "major":
          actually_updatable.append({ 'reference': image['reference'], 'repository': image['parts']['repository'] })
        elif 'type' in image['result']['info'] and image['result']['info']['type'] == "digest":
          actually_updatable.append({ 'reference': image['reference'], 'repository': image['parts']['repository'] })
    
    print(f"Redeploying {len(actually_updatable)} container(s)..")
    for image in actually_updatable:
      ansible_tag = search_for_image(image['repository'])
      print(ansible_tag, image['reference'])
      if ansible_tag and ansible_tag in deployable_tags and ansible_tag not in already_deployed:
        print(f'[UPDATE] Deploying {ansible_tag}..')
        subprocess.run(f'ANSIBLE_CONFIG=ansible.cfg ansible-playbook main.yml --tags {ansible_tag} --vault-password-file=~/.vault_pass.txt', shell=True)
      else:
        print('[UPDATE] Could not find corresponding task, cleaning up..')
        subprocess.run(f"docker image remove {image['reference']}", shell=True)
      already_deployed.append(ansible_tag)

    print("\nAll images updated, refreshing Cup")
    requests.get("https://cup.fntz.net/api/v3/refresh")
  else:
    print("No images to update!")

if __name__ == "__main__":
  main()
