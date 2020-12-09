# Promotions

[![Build Status](https://travis-ci.org/2020-nyu-devops/promotions.svg?branch=master)](https://travis-ci.org/2020-nyu-devops/promotions)
[![codecov](https://codecov.io/gh/2020-nyu-devops/promotions/branch/master/graph/badge.svg?token=N3CA84MPTL)](https://codecov.io/gh/2020-nyu-devops/promotions/)

This repository is part of the NYU class **CSCI-GA.2810-001: DevOps and Agile Methodologies** taught by John Rofrano, Adjunct Instructor, NYU Curant Institute, Graduate Division, Computer Science. It contains the work done by the promotions squad for this class in fall of 2020.

## Overview

This is the repository that houses the code to implement promotions on an eCommerce shop.

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
requirements.txt    - list if Python libraries required by your code
Vagrantfile         - Vagrant file that installs Python 3
app.py              - a Python file that builds a Flask application that simply returns "Hello World"
```

## Building Locally

### Vagrant

You will need to download and install [VirtualBox](https://www.virtualbox.org/) and [Vagrant](https://www.vagrantup.com/). Then clone this repository to your computer, and invoke vagrant:

```bash
    git clone git@github.com:2020-nyu-devops/promotions.git
    cd promotions
    vagrant up
    vagrant ssh
    cd /vagrant
```

To run the service use `flask run` (Press Ctrl+C to exit):

```bash
  $ FLASK_APP=service:app flask run -h 0.0.0.0
```

You must pass the parameters `-h 0.0.0.0` to have it listed on all network adapters to that the post can be forwarded by `vagrant` to your host computer so that you can open the web page in a local browser at: http://localhost:5000. When you are done, you should exit the virtual machine and shut down the vm with:

```bash
 $ exit
 $ vagrant halt
```

If the VM is no longer needed you can remove it with:

```bash
  $ vagrant destroy
```

### Manual install using local Python

If you have Python 3 installed on your computer you can make a virtual environment and run the code locally with:

```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    FLASK_APP=app flask run
```

## Manually running the Tests

Run the tests using `nose`

```shell
    $ nosetests
```

Nose is configured via the included `setup.cfg` file to automatically include the flags `--with-spec --spec-color` so that red-green-refactor is meaningful. If you are in a command shell that supports colors, passing tests will be green while failing tests will be red.

Nose is also configured to automatically run the `coverage` tool and you should see a percentage of coverage report at the end of your tests. If you want to see what lines of code were not tested use:

```shell
    $ coverage report -m
```

This is particularly useful because it reports the line numbers for the code that is not covered so that you can write more test cases to get higher code coverage.

You can also manually run `nosetests` with `coverage` (but `setup.cfg` does this already)

```shell
    $ nosetests --with-coverage --cover-package=service
```

Try and get as close to 100% coverage as you can.


## Deploy to IBM Cloud manually
The `manifest.yml` file must be edited with the configuration of the cloud where is application is to be deployed to.

Add the `apiKey.json` file to a new directory `.bluemix` in the folder. This should enable logging into your IBM Cloud to deploy the application.

Invoke Vagrant and log into IBM Cloud using the following commands.

``` shell
    $ vagrant up
    $ ibmcloud login -a https://cloud.ibm.com --apikey @~/.bluemix/apiKey.json -r <region> -o <organization> -s <space> 
``` 

Ensure that the ElephantSQL URL is present in the `VCAP_SERVICES` environment variable of the runtime of the Cloud Foundry application.

From the root directory of the application code execute the following to deploy the application to the IBM Cloud. 

```bash
$ ic cf push <YOUR_APP_NAME>
```

### View App
Once the application is deployed and started, open a web browser and point to the application route defined at the end of the `cf push` command. This will execute the code under the `/` app route defined in the `server.py` file. Navigate to `/promotions` to see a list of promotions returned as JSON objects.



## Endpoints

| Request Type | Endpoint                      | Description                                                                                       |
| ------------ | ----------------------------- | ------------------------------------------------------------------------------------------------- |
| ```GET```    | ```/promotions```             | List all promotions or query based on certain parameters.                                         |
| ```GET```    | ```/promotions/<id>```        | Get a specific promotion based on its ID                                                          |
| ```POST```   | ```/promotions```             | Creates a promotion with information in request body                                              |
| ```PUT```    | ```/promotions/<id>```        | Updates a promotion with information in request body                                              |
| ```DELETE``` | ```/promotions/<id>```        | Deletes a promotion based on its ID                                                               |
| ```POST```   | ```/promotions/cancel/<id>``` | Cancels a promotion based on its ID                                                               |
| ```GET```    | ```/promotions/apply```       | Applies best promotion available to the list of products. Returns which promo-code to be applied. |

#### Query Parameters

| Parameter          | Description                                                                                                                                |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| ```amount```       | Filter the results based on the amount of discount                                                                                         |
| ```is_site_wide``` | Filter the results based on whether the promotion is available for the entire store                                                        |
| ```promo_code```   | Filter the results for a particular Promo Code                                                                                             |
| ```promo_type```   | Filter the results for a particular Promo Type                                                                                             |
| ```start_date```   | Filter the results based on a start date.                                                                                                  |
| ```end_date```     | Filter the results based on an end date.                                                                                                   |
| ``` duration```    | Filter the results based on the duration (in days) of a promotion. For example, filter out all the ads with duration greater than 10 days. |

##### Date Format

Dates for promotions look like: 

```Sat, 17 Oct 2020 00:00:00 GMT```


##### Promo Types 

There are 3 different types of promotions we currently offer:

```text
BOGO # buy one product get one free
DISCOUNT # fixed % off
FIXED # set $ amount off
```

## Acknowledgements

The code structure, templating, and environment files are modified from this repository: https://github.com/nyu-devops/project-template.
