#!/usr/bin/env python3

from pathlib import Path
import json
import sys
import os


SUPPORTED_METADATA_VERSION = 1

paths = []
output = {}

for arg in sys.argv[1:]:
  if os.path.isdir(arg):
    for path in Path(arg).rglob('*.json'):
      paths.append(path)
  elif os.path.isfile(arg) and arg.endswith('.json'):
    paths.append(arg)
  else:
    sys.stderr.write("Not a directory and not a .json file: {} => abort\n".format(arg))
    exit(1)


def collect_names(images):
  names = []
  for image in images:
    names.append(image['name'])
  return names

for path in paths:
  with open(path, "r") as file:
    try:
      obj = json.load(file)

      if obj['metadata_version'] != SUPPORTED_METADATA_VERSION:
        sys.stderr.write('{} has unsupported metadata version: {} => skip\n'.format(path, obj['metadata_version']))
        continue

      version = obj['version_number']
      commit = obj['version_commit']

      if not version in output:
        output[version] = {'link': '', 'commit':  commit, 'models' : []}

      # only support a version_number with images of one version_commit
      if output[version]['commit'] != commit:
        sys.stderr.write('mixed revisions for a release ({} and {}) => abort\n'.format(output[version]['commit'], commit))
        exit(1)

      for title in obj['titles']:
        if 'title' in title:
          output[version]['models'].append(['', title['title'], '', obj['target'], collect_names(obj['images'])])
        else:
          output[version]['models'].append([title.get('vendor', ''), title['model'], title.get('variant', ''), obj['target'], collect_names(obj['images'])])

    except json.decoder.JSONDecodeError as e:
      sys.stderr.write("Skip {}\n   {}\n".format(path, e))
      continue
    except KeyError as e:
      sys.stderr.write("Abort on {}\n   Missing key {}\n".format(path, e))
      exit(1)

json.dump(output, sys.stdout, sort_keys=True)
#json.dump(output, sys.stdout, sort_keys=True, indent="  ")
