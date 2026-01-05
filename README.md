# shabunble
Shareable unenterable docker images

- [What is this?](#what-is-this)
- [Quick Start Guide](#quick-start-guide)
- [Step by step guide](#a-guide-to-make-them-stumble-with-shabunble)
  - [Basic example](#basic-example)
  - [Extended example](#more-meaty-example)
  - [When the shell is neccesary](#what-to-do-when-you-need-a-shell-in-the-deployment-stage)
- [The general idea](#the-practical-proposal)
- [Dependencies](#dependencies)
- [Current state of the project](#current-state-in-the-pursuit-of-perfection-not-the-practical)
- [Next step for the project](#next-step)

## What is this?
This repo is the artifact of the work put into creating shareable uninspectable running code. This would at first glance seem quite easy to do, a notion I attribute to the opaqueness of the fundamental machine to us as programmers and computer users; the brute force burden of computation and the mindnumbing minutiae of electronic plumbing is abstracted away letting us interact with it on human terms. But, when we don't delude ourselves into thinking that our own ignorance is meritted by an inherent ineffability native to the world, we know that computing is just math. And math doesn't lie.

If the computer can calculate it, it is part of the computers whole computation. Code cannot be at once parseable and hidden. Any boundary we set on the computations in the computer is itself part of the computations. These statements represent my current understanding of this topic, and from this a simpler statement: I believe that it is impossible to at once run code on a computer while making that code uninspectable.

But I also believe that we don't truly have to make the code uninspectable, just sufficiently hard to inspect. Novel solutions like fully homomorphic encryption or specialised confidential computing hardware might deter even the highly motivated. But in most cases we should be able to get away with utilizing the notion of opagueness mentioned earlier. If we just make it slightly harder to inspect the code at the expected level of asbtraction, then I expect that we'll stymie a good portion of unwanted inspections.

Thus, my current proposal while I look for something stronger.

## Quick Start Guide

Create Docker containers that discourage casual inspection using multi-stage builds:

### Step 1: Build in a Full Environment

Use a standard image with all development tools:

```dockerfile
FROM python:3-slim AS build-env
COPY ./app /app
WORKDIR /app
```

### Step 2: Deploy in a Minimal Environment

Copy only what's needed to a distroless image:

```dockerfile
FROM gcr.io/distroless/python3
COPY --from=build-env /app /app
WORKDIR /app
CMD ["app.py"]
```

### Step 3: Handle Dependencies (if needed)

For Python packages, use a virtual environment:

```dockerfile
# In build stage
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install -r requirements.txt

# In deployment stage, copy the venv
COPY --from=build-env /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/opt/venv/lib/python3.11/site-packages"
```

### Step 4: Build and Run

```bash
docker build -t myapp .
docker run -t myapp
```

**Note**: These techniques create "speed bumps" not security. See the detailed guide below for limitations.

## A guide to make them stumble with shabunble
One of the most common ways to enter and inspect a docker container is to simply shell into it. So we want to make that hard to do.

We'll be taking advantage of the fact that docker images can be build in [multiple stages](https://docs.docker.com/build/building/multi-stage/) to build our app in a tool-rich environment and deploy it in a tool-sparse environment, ideally an environment without a shell.

(If the shell is an important part of your application - if it is dependent on shell scripts at runtime for example - then we'll just ensure that all of the other shell conveniences - like f.x. "cd", "ls", "find" or "grep" - aren't present.)

Doing this is a simple 3 step process:
**1 -** Determine the minimal image needed to build the application.
**2 -** Determine the minimal image needed to *deploy* the application.
**3 -** Write a docker file that first builds the application in the build image, then copies it over to the deployment image and sets the entrypoint there.

To show what I mean by this, let us start out with a very basic example, and afterwards follow that up with a more meaty example.

### *Basic example*
I have a [small python app](enterable_container/python_app/app.py) that runs in the terminal. It counts down from 10 and then shows some ascii art. It has no real dependencies other than python itself. To deploy I "naïvely" made a simple [dockerfile](enterable_container/Dockerfile) that builds ontop of the [python:3-slim](https://hub.docker.com/layers/library/python/3-slim/images/sha256-c0634a83210c540f4972cbc3e8a7baa6868a4d0fc019d44a2f74f28abe0d0a89) image.

So, **first step**, what is the minimal image that I need to build this app? well, there isn't much building actually happening as all the dockerfile does is copy the python script from the host machine. But, the current base image certainly is capable of being copied to, and keeping this part minimal is more for the sake of keeping the total image small, so I'm sticking with my already known image, python:3-slim, as the build image.

In general, if you already have a working (single stage) docker container, that containers base image will work as your build image.

For the **second step** I know that my app requires nothing more than a python interpreter, and a place for sys.stdout to point to. python:3-slim has that, but it also has a lot of other unnecessary "cruft" like the shell we would rather be without. We need something slimmer. Something less than what is usually distributed.

Well, it just so happens that Google creates and maintains a repository of [distroless](https://github.com/GoogleContainerTools/distroless) container images, which are designed to run a singular app and nothing else. They have a variety of images for different usecases, one of which is just running a python app. This [image](gcr.io/distroless/python3) is what I'll be using as my *deployment* image.

Finally, the **third step** is quite trivial in this case; the second deployment image is added to the dockerfile from before, all files from the build stage is copied to the deployment stage, and the app is still set as the entrypont (although the syntax is [subtly different](https://github.com/GoogleContainerTools/distroless?tab=readme-ov-file#entrypoints) as the entrypoint is executed without a shell).

Thus we have our ["unenterable" dockerfile](unenterable_container/Dockerfile)!

Now, in this basic example, there was next to nothing to the third step. In truth both it and the build stage could have been entirely omitted by just copying the app directly from the host system to the deployment stage. In most real cases, this would have proven a bit more envolved. To show this, let us go to the more meaty example.

### *More meaty example*
I again have a [python app](unenterable_neural_network/classifier.py), but this one contains a neural network and depends on both pytorch and influxdb. When the image is running it connects to a database in the containing environment and classifies the data as it is fed to that database. The neural network is pretrained and the weights are thus packaged with the image.
The weights, ofcourse, are the part we really want to safeguard.

Again, our [unprotected dockerfile](unenterable_neural_network/unobfuscated/Dockerfile) builds on the [python:3-slim](https://hub.docker.com/layers/library/python/3-slim/images/sha256-c0634a83210c540f4972cbc3e8a7baa6868a4d0fc019d44a2f74f28abe0d0a89) image.

Our **first** and **second** steps are the same as for the basic example. This time we actually need the python slim image for the build stage as we need to install both the pytorch and influxdb-client packages. But for running we still only need the python interpreter, so the [distroless python image](gcr.io/distroless/python3) will still do the trick.

The **third step** is where we now have get *slightly* creative. We need the **deployment stage** to have not only the python interpreter, but also the python packages. The stock interpreter in the distroless image has nothing but standard stuff. The easiest way to do this is to create a virtual environment in the **build stage**, install the neccesary packages into that virtual environment, copy it over to the **deployment stage** and change the python path to point towards the python binary in our virtual environment. This ends up looking [like so](unenterable_neural_network/shellless/Dockerfile), and voila, we have a classifer without a pesky shell to inspect it!

### *What to do when you need a shell in the deployment stage*
Sometimes a POSIX compliant shell and its standard porgrams are just too convenient at deployment to be completely without them. Maybe some part of execution is dependent on an ad hoc shell script. Maybe part of the application needs to interact with some external API using curl. Whatever the reason, a barebones [distroless](https://github.com/GoogleContainerTools/distroless) image is just too restrictive. What to do?

Well, what we want to do is to make the shell that we can't do without useless for anyone but ourselves. We do this by removing all of the programs that are otherwise ubiquitous in the shell.

First, pick a minimal image that still has a shell (if you are following the three steps outline earlier, this would be the **second step**). Then, **remove all of the programs that you won't need**. Need `curl` and `mkdir`? Nothing else? Well then remove things like `ls`, `cd` and any packagemanagers like `apt` from the `/bin` folder. Same goes for `find`, `grep` and all of the other standard programs. You won't be needing them, and so there is no reason to let them stay around for any potential snooper.

This is a bit more elaborate than just basing the deployment stage on a distroless image, but it really isn't harder than just adding the line
```
EXEC rm /bin/ls && rm /bin/cd && <and so on an so forth> 
```
to your dockerfile in the deployment stage. Some trial and error might be required to figure out what is and isn't used.

## The Practical Proposal
Docker images contain all the files needed to run a program along with meatadata describing how the image should be instantiated. When instantiating the image, a user can choose to overwrite the defaults set by this metadata, letting them run other code present in the image. This is useful if a user wants to inspect the image as they can instantiate it with a shell and do all the tasks that one normally would be able to when shelled into a computer.

But, if there is no shell binary present in the image, then it can't be instantiated with a shell. The same goes for other unwanted programs and operations. Thus if we build the image with only the barest of neccesities to run our code, then users can't run anything unwanted without modifying the image first in some way.

(Modifying the image is not hard, but we are banking on most users simply not knowing that that is a possibility.)

So here is what we do. We split the build of the image into two parts. In the first part we build the code, and we do this in an image with all the tools we need to do so (a shell, curl, package managers, whatever is needed). Then we copy only the essential code (binaries, scripts and other assets) into the second part, which is based off of an image with only the bare necessities to run our code. Nothing else.

In the subdirectory `/unenterable_container` I have included the Dockerfile for an minimal example of this for a simple python app. In this toy example the first part of the build doesn't actually do anything other than copying the python code from the surrounding environment (it is simple python, so nothing needs to be compiled). But the second part that is the interesting one anyway. In it, I start with one of googles "distroless" images, and copy the python code over to it before setting the python code as the entrypoint for the image. Googles "distroless" images (available at https://github.com/GoogleContainerTools/distroless) have several flavors meant to run only one flavor of interpreted language (and others that only run compiled binaries) with no other ancillirary programs. This makes it hard to run anything but the intended entry point (in the toy example all entrypoints must be python code, and our app is the only python code present), a great boon, but also a great limitation. The final image is much more limited, is tailored for a specific use case and is ill suited for hybrid code bases with multiple interpreted languages.

Generally, the proposal hinges on having seperate build and deploy stages in the dockerfile and ensuring that the deploy stage is based on an image with only the bare necessities, which can either be a "distroless" image from google or other providers, or an image build completely from scratch.

## Dependencies
This whole project is currently based on [Docker](https://www.docker.com/), so you'd need at least that for this to make any sense.
On top of this, the few examples I've made are Python based (specifically [python 3.11](https://www.python.org/downloads/release/python-31114/), but other versions might do too).
Finally, this work is all done from a Linux based OS, but all of the work done here is currently OS agnostic at its core. That being said, some of the examples assume that the host OS is Linux, and some commands might have to be changed to suit Windows, MacOS or whatever you are running with.

## Current state (in the pursuit of perfection, not the practical)
I've managed to create a simple python app in a container that writes some silly stuff to the terminal without having a built in shell.
The Dockerfile and related sources are located in `/unenterable_container` if you want to try out the image.

That being said a container image is NOT an obfuscated file format. It is essentially a file structure (often tarred and compressed) with some metadata. Entering it is trivial (just unpack it). Protocol demands that they be immutable, but nothing stops an importer of an image from inspecting and mutating it BEFORE instantiating it.

This means that we can modify the image before running it to include a shell, voiding the "security advantage" of building a shell-less image.

For example:
The image build from the Dockerfile in `/unenterable_container` is based on the python version of Google's "distroless" images. This means that it boots directly into python, potentially running the python script that is set as the entrypoint. In the Dockerfile this is set to be the small python app copied from `/unenterable_container/python_app`. This app repeatedly counts down from 10 and shows an ASCII image of an explosion, taking no input. Stopping it stops the whole container. But we can change the entrypoint as part of the `docker run` command, pointing it to a more usefull python app. No other app is on the image by default, but we can also specify a directory to be mounted on the image as part of the `docker run` command. Say, for instance, a directory containing a shell written in python called `mount_injection`.
From the repository root:
```
cd unenterable_container
docker build -t unenterable_boomline .
docker run -it -v $PWD/../mount_injection:/injection unenterable_boomline /injection/python_shell.py
```
The example python shell is very barebones, and several standard linux commands (like ls) are not present in the distroless image. But python is obviously a possible command, so at least we can run the original python app:
```
python app.py
```
And if we have any other tools we want to use, we can add them as part of the mounted injection directory.

## Next step
Looking into confidential computing.


#### A log, I guess
Setting users in the Dockerfile does nothing to hinder importers of the image; it restricts the permissions of the processes running **inside** the container, but someone outside the container still have the permissions of the user they are logged in as. If that user has sufficient permissions from the host computer to `docker run <IMAGE>`, then it doesn't matter what the standard entrypoint or user has been defined as in the Dockerfile; these can be overwritten as part of the `docker run` command: `docker run --entrypoint=sh user=root -it <IMAGE>`. (`enterable_container` contains a simple Dockerfile for an image with a user and defined entrypoint for testing this.)

I followed this unconference talk by Eric Chiang: https://ericchiang.github.io/post/containers-from-scratch/

Further reading: https://github.com/coollog/build-containers-the-hard-way

A container image is simple to inspect and edit - it is just nested directories with metadata. There is no encryption, there is no obfuscation (other than knowing the docker or OCI image standard).