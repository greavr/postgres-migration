# Postgres Migrate Sample
[![License](https://img.shields.io/badge/License-apache-blue.svg)](LICENSE.md)

## Overview
<a id="Overview"></a>

This is a sample workload which demonstrates how you can synchronize DB records from [CloudSQL](https://cloud.google.com/sql) to [AlloyDB](https://cloud.google.com/alloydb) using [Cloud DMS](https://cloud.google.com/database-migration).
- [CloudSQL](https://cloud.google.com/sql) - Cloud SQL manages your databases so you don't have to, so your business can run without disruption. It automates all your backups, replication, patches, encryption, and storage capacity increases
- [AlloyDB](https://cloud.google.com/alloydb) - A fully managed PostgreSQL—compatible database service for your most demanding enterprise workloads. AlloyDB combines the best of Google with PostgreSQL, for superior performance, scale, and availability.
- [Cloud DMS](https://cloud.google.com/database-migration) (Database Migration Service) - A managed service to handle the migration of data between database solution

To help simulate migration during use there are two small sample applications running inside containers managed by [GKE Autopilot](https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview). GKE Autopilot is a mode of operation in GKE in which Google manages your cluster configuration, including your nodes, scaling, security, and other preconfigured settings. The writer part of the application preforms random updates to the [sample database provided by PostgreSQL (DVD Rentals)](https://www.postgresqltutorial.com/postgresql-getting-started/postgresql-sample-database/) hosted on CloudSQL. A second application, reader, checks both the source Cloud SQL and the target AlloyDB instances to show a per table record count. 
Cloud DMS is used to continuous replicate the data from CloudSQL to AlloyDB. This is currently configured for one way replication, but it can be configured for two way synchronization.

There are several additional components used to simplify application:
- [Cloud Secret Manager](https://cloud.google.com/security/products/secret-manager) - Used to store the Database Credentials. [We can map secrets from the managed secret service into the POD as kubernetes secrets](https://cloud.google.com/kubernetes-engine/docs/tutorials/workload-identity-secrets)
 - [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity) - Used to embed service accounts into the environment, [enabling workloads to access Google Cloud products and features with dynamic service account credentials](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity#authenticating_to).
- [AlloyDB Auth Proxy](https://cloud.google.com/alloydb/docs/auth-proxy/overview) - Used to simplify connections from the Reader Pod to the AlloyDB instance. There is also a [CloudSQL Auth Proxy too](https://cloud.google.com/sql/docs/postgres/sql-proxy), however this use case focused on utilization of GKE Autopilot and AlloyDB. Both of the proxy agents can be run in docker, or CLI.

**Additional things of point are:**
- [Cloud SQL Plugin Enablement](https://cloud.google.com/sql/docs/postgres/extensions) - This requires a reboot when configure
- [AlloyDB Plugin Enablement](https://cloud.google.com/alloydb/docs/reference/extensions) - This requires a reboot when configured



## Table of Contents
- [Overview](#overview)
- [Network Diagram](#network-diagram)
- [Installation](#installation)
- [Prerequisites](#prerequisites)
- [Tool Setup Guide](#tool-setup-guide)


## Network Diagram
<a id="network-diagram"></a>
![Network Diagram](./images/architecture.jpg)

## Installation
<a id="installation"></a>
Terraform will be used to deploy the entire application, however there are still some manual steps (install the sample DB for example)

## Prerequisites
<a id="prerequisites"></a>
GCP Project With Billing Enabled
- Your user account will need permissions to:
- Enable API for GCP Services
- Provision CloudSQL instances
- Provision AlloyDB Instances
- Provision GKE Clusters
- Provision Cloud DMS workflows
- Provision and manage Cloud Secrets
- Provision VPC Networks (or use existing shared VPC)
- Configure VPC networks
- Create Service Accounts
- Recommendation is that you get Project Owner role


## Tool Setup Guide
<a id="tool-setup-guide"></a>
[Tool Install Guide](tools/ReadMe.md)