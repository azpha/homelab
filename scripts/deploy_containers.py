import sys
import os
import subprocess

vpn_containers = [ # containers that need to be recreated re: vpn
  "tasks/qbittorrent.yml",
  "tasks/jackett.yml"
]
ignore_deploys_for = [ # don't auto-deploy these
  "tasks/runner",
  "templates/runner",
  "roles/docker"
]

def git_diff():
  args = sys.argv
  res = subprocess.run(f"git diff --name-only {args[1]} {args[2]}", capture_output=True, shell=True, text=True)
  return [x for x in res.stdout.strip().split("\n") if "tasks/" in x or "roles/" in x or "templates/" in x]

def construct_command(tags):
  command = f"ANSIBLE_CONFIG=ansible.cfg /usr/bin/ansible-playbook main.yml --tags={",".join(tags)} --vault-password-file ~/.vault_pass.txt"
  print(command)
  return command

def deploy(tags):
  print(f"[MAIN] Deploying...")
  command = construct_command(tags)
  res = subprocess.run(command, shell=True)
  return res.returncode == 0

def get_normalized_task_name(container):
  if "tasks/" in container:
    task_name = container.split("/")[1].split(".")[0]
  elif "roles/" or "templates/" in container:
    task_name = container.split("/")[1]
  else:
    task_name = False

  return task_name


def main():
  dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')
  diff = git_diff()
  deployable_containers = []
  removable_containers = []

  for file in diff:
    if os.path.exists(os.path.join(dir_path, file)):
      deployable_containers.append(file)
    else:
      removable_containers.append(file)

  print(f"[MAIN] Deployable: {deployable_containers}")
  print(f"[MAIN] Removable: {removable_containers}")

  if len(deployable_containers) > 0:
    to_deploy = []
    for container in deployable_containers:
      task_name = get_normalized_task_name(container)
      if task_name:
        to_deploy.append(task_name + "_deploy")
      
    if len(to_deploy) > 0:
      result = deploy(to_deploy)

  if len(removable_containers) > 0:
    for container in removable_containers:
      task_name = get_normalized_task_name(container)
      result = subprocess.run(
        f'/usr/bin/docker ps --filter "name={task_name}" -q',
        shell=True,
        capture_output=True
      )
      for line in result.stdout.splitlines():
        container_id = line.strip().decode("utf8")
        if not container_id:
            continue
        print(f"[MAIN] Found Docker container {container_id} related to {task_name}, removing..")
        subprocess.run(f"/usr/bin/docker container stop {container_id}", shell=True)
        subprocess.run(f"/usr/bin/docker container rm {container_id}", shell=True)
        subprocess.run("/usr/bin/docker image prune -f", shell=True)
        subprocess.run("/usr/bin/docker container prune -f", shell=True)

if __name__ == "__main__":
  main()