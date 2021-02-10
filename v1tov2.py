#!/usr/bin/python3

import argparse
import ruamel.yaml
import sys
import yaml
from pathlib import Path

arg_parser = argparse.ArgumentParser( description = "Generate fluxV2 target_file file from fluxV1 source_file, also sourcefile for generated fluxv2 release as git-helm-source file" )
arg_parser.add_argument( "source_file" )
arg_parser.add_argument( "target_file" )
arg_parser.add_argument( "git_helm_file" )
arguments = arg_parser.parse_args()

source = arguments.source_file
target = arguments.target_file
git_helm = arguments.git_helm_file
# print( "Copying [{}] to [{}]".format(source, target) )

fp = open(source, 'r')
yaml = ruamel.yaml.YAML()
yaml.preserve_quotes = True

config, ind, bsi = ruamel.yaml.util.load_yaml_guess_indent(open(source))
metadata, ind, bsi = ruamel.yaml.util.load_yaml_guess_indent(open(source))

spec = config['spec']
metadata = metadata['metadata']
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

# print(namespaceName)
# print("heyyy")
# if spec['chart']['repository'] in source:
#     spec['chart']['spec']['chart'] = spec['chart']['name']
# spec['chart']['name'] = 'Username'
# spec['chart']['version'] = 'Password'
fp = open(source, 'r')
file_name = Path(source)
# {'chart':{'spec':{'chart':'minio', 'version':'8.0.7'}}}
# record_to_add1 = {'spec':{'chart':chartName, 'version': versionName, 'sourceRef':{'kind':'HelmRepository', 'name': repoName, 'namespace': namespaceName}}}
# record_to_add2 = {'spec':{'chart':chartName, 'sourceRef':{'kind':'GitRepository', 'name': repoName, 'namespace': namespaceName}}}
yaml = ruamel.yaml.YAML()
yaml.explicit_start = True
data = yaml.load(file_name)
data['apiVersion'] = 'helm.toolkit.fluxcd.io/v2beta1'
data['metadata']['annotations'] = None

# if 'repository1' in fp.read():
#     print("hello3")
#     data['spec']['chart'] = record_to_add1
if 'git:' in fp.read():
    print("hello4 creating git source")
    data['spec']['chart'] = record_to_add2
else:
    print("hello3 creating helm source")
    data['spec']['chart'] = record_to_add1

# data['spec']['interval'] = '1m'
# yaml.dump(data, sys.stdout)
# stream = open(source, 'r')
# data = yaml.load(stream)
# # if spec['chart']['repository'] in source:
# #     spec['chart']['spec']['chart'] = spec['chart']['name']
# data['apiVersion'] = 'helm.toolkit.fluxcd.io/v2beta1'
# data['spec']['chart']['name'] = 'Username'
# data['spec']['chart']['version'] = 'Password'

# with open(source) as fp:
#     data = yaml.load(fp)
# for elem in data:
#     print(elem)
#     # if elem['repository'] == 'https://helm.min.io/':
#     #      elem['version'] = 1234
#     #      break  # no need to iterate further
# yaml.dump(data, sys.stdout)
with open(target, 'w') as fp:
    yaml.dump(data, fp)


