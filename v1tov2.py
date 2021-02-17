#!/usr/bin/python3

import argparse
import ruamel.yaml
import sys
import yaml
from pathlib import Path

arg_parser = argparse.ArgumentParser( description = "Generate fluxV2 target_file file from fluxV1 source_file, also sourcefile for generated fluxv2 release as git/helm-source file" )
arg_parser.add_argument( "source_file" )
arg_parser.add_argument( "target_file" )
arg_parser.add_argument( "git_helm_file" )
arguments = arg_parser.parse_args()

source = arguments.source_file
target = arguments.target_file
git_helm = arguments.git_helm_file

fp = open(source, 'r')
yaml = ruamel.yaml.YAML()
yaml.preserve_quotes = True

config1, ind, bsi = ruamel.yaml.util.load_yaml_guess_indent(open(source))
config2, ind, bsi = ruamel.yaml.util.load_yaml_guess_indent(open(source))

spec = config1['spec']
metadata = config2['metadata']
namespaceName = metadata['namespace']
repoName = namespaceName + "-repository"
if 'git:' in fp.read():
    print("hello2 found git")
    chartName = spec['chart']['path']
    record_to_add2 = {'spec':{'chart':chartName, 'sourceRef':{'kind':'GitRepository', 'name': repoName, 'namespace': namespaceName}}}
    gitUrl = spec['chart']['git']
    gitRef = spec['chart']['ref']
    create_git_source = {   'apiVersion': 'source.toolkit.fluxcd.io/v1beta1',
                            'kind': 'GitRepository',
                            'metadata': {'name': repoName, 'namespace': namespaceName},
                            'spec': {'interval': '1m',
                                    'ref': {'branch': gitRef},
                                    'url': gitUrl}}
    
    with open(git_helm, 'w') as f:
        yaml.dump(create_git_source, f)

else:
    print("hello1 found helm")
    chartName = spec['chart']['name']
    versionName = spec['chart']['version']
    record_to_add1 = {'spec':{'chart':chartName, 'version': versionName, 'sourceRef':{'kind':'HelmRepository', 'name': repoName, 'namespace': namespaceName}}}
    helmUrl = spec['chart']['repository']
    create_helm_source = {  'apiVersion': 'source.toolkit.fluxcd.io/v1beta1',
                            'kind': 'HelmRepository',
                            'metadata': {'name': repoName, 'namespace': namespaceName},
                            'spec': {'interval': '1m', 'url': helmUrl}}
    
    with open(git_helm, 'w') as f:
        yaml.dump(create_helm_source, f)


fp = open(source, 'r')
file_name = Path(source)
yaml = ruamel.yaml.YAML()
yaml.explicit_start = True
data = yaml.load(file_name)
data['apiVersion'] = 'helm.toolkit.fluxcd.io/v2beta1'
data['metadata']['annotations'] = None
data['spec'].insert(1, 'interval','1m')

# del data['spec']['maxHistory']
# del data['spec']['rollback']
# del data['spec']['helmVersion']
# del data['spec']['annotations']
# if 'helmVersion:' in fp.read():
#     del data['spec']['helmVersion']
# if 'maxHistory:' in fp.read():
#     del data['spec']['maxHistory']
# if 'rollback:' in fp.read():
#     del data['spec']['rollback']

if 'git:' in fp.read():
    print("hello4 creating git source")
    data['spec']['chart'] = record_to_add2
else:
    print("hello3 creating helm source")
    data['spec']['chart'] = record_to_add1

with open(target, 'w') as fp:
    yaml.dump(data, fp)

