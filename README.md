Locksmith Agent
===============

Simple locking client for use with locksmith-server

This aims to imitate the functionality of using flock and local files but on a
network with multiple clients and no access to shared FS.

Requirements
------------

 * Python (2.7 tested)
 * requests

Installation
------------

```sh
$ pip install git+git://github.com/fim/locksmith-agent.git
```

Usage
-----

 * Register with your lock server

```sh
$ locksmith register http://lock-server
```

 * Acquire locks

```sh
$ locksmith lock foo
```
 * Release locks

```sh
$ locksmith unlock foo
```

 * Execute something when lock is acquired

```sh
$ locksmith execute -l foo "ls -la"
```
