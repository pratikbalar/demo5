## This repo contains the migration demo from Fluxv1 to Fluxv2

### In order to perform the exercise execute the below commands and take care of the notes

#### First we will run all the releases by the help of Fluxv1, for that

```
kubectl apply -f https://raw.githubusercontent.com/fluxcd/helm-operator/master/deploy/crds.yaml
```

```
-  helm upgrade -i flux fluxcd/flux \
   --set git.url=git@github.com:dharmendrakariya/demo5 \
   --namespace flux \
   --set git.path=fluxv1/


-   helm upgrade -i helm-operator fluxcd/helm-operator \
   --set git.ssh.secretName=flux-git-deploy \
   --namespace flux --set helm.versions=v3

```

In another trminal open ```k9s --all-namespaces``` and see all the helmreleases are deployed.

After that, for the migration process, scale down the flux/helm-operator

``` kc scale deployment -n flux --replicas=0 flux ```

``` kc scale deployment -n flux --replicas=0 flux-memcached ```

``` kc scale deployment -n flux --replicas=0 helm-operator ```

note: just in case if you want clean way, you can delete flux at all. 

```helm uninstall -n flux flux```

```helm uninstall -n flux helm-operator```


#### If you want to use flux cli you can use below commands, but we won't be using Flux cli so we are skippin this.

```
export GITHUB_TOKEN=YOUR PAT TOKEN


   flux bootstrap github \
  --owner=dharmendrakariya \
  --repository=demo5 \
  --path=fluxv2 \
  --personal \
  --branch=master
```

#### In order to bootstrap your repo without using Flux cli, execute below commands

Create flux-system namespace 

```kc apply -f fluxv2/flux-system/namespace_flux-system.yaml```

Create flux-system secret, which has deploy key identity.pub, which supposed to be added to your repo

note: add this key as soon as you create the secret, it supposed to be added before git_repo_sync creation, bcoz as soon as repo gets configured, it tries to sync it and if it doesn't find the key, it will remove those old deployments. (anyway no harm in adding it first)

to generate the secret we can use flux cli, it has command 

```
flux create secret git flux-system \
    --url=ssh://git@github.com/dharmendrakariya/demo5 \
    --export > secret_flux-system.yaml
```
but we ```should```  use  ```ssh-keygen -t rsa``` command which allows us to create private/public key pair.

add private and public key in secret-flux-system file and for github public fingerprint use belwo command

```ssh-keyscan -t rsa github.com | tee github-key-temp | ssh-keygen -lf -```

which will generate github-key-temp file, this command takes public fingerprint provided by [github](https://docs.github.com/en/github/authenticating-to-github/githubs-ssh-key-fingerprints). copy the content and paste it under known-host field in secret-flux-system file.


```kc apply -f fluxv2/flux-system/secret_flux-system.yaml```

Apply crds

```kc apply -f fluxv2/flux-system/flux_toolkit_v0.7.7.yaml```

Add git repo to be synced

```kc apply -f fluxv2/flux-system/git_repo_sync.yaml```

Now see in other k9s that nothing is being redeployed and also watch new helmreleases being created and geting reconciliation succeeded


##### Notes:

I have faced [this](https://github.com/fluxcd/flux2/issues/811#issuecomment-778014491) problem make sure you define namespace in new releases.

I have python script v1tov2.py which takes three args, 1st the fluxv1 file which should be converted to fluxv2 file, 2nd the name to be set for generated fluxv2 file, 3rd the source-file of newley generated fluxv2 file.

example:

python v1tov2.py old-release.yaml new-release.yaml git-source.yaml

make sure you have 

```
spec:
   interval: 1m
```

and remove below stuff from new release,if it took these from old release, as those are changed in new(fluxv2) api

```
   helmVersion: v3
   maxHistory: 3
   rollback:
     enable: true
     retry: true
     maxRetries: 3
```

After these changes you are good to go