---
description: A brief overview of the components provided by the Orion orchestration engine and API.
tags:
    - Orion
    - work queues
    - agents
    - orchestration
    - database
    - API
    - UI
    - storage
---

# Flow orchestration with Orion

Up to this point, we've demonstrated running Prefect flows and tasks in a local environment using the ephemeral Orion API. As you've seen, it's possible to run flexible, sophisticated workflows in this way without any further configuration.

Many users find running flows locally is useful for development, testing, and one-off or occasional workflow execution.

Where you begin leveraging the full power of Prefect is flow orchestration &mdash; building, running, and monitoring your workflows at scale.

Orchestration with Prefect helps you schedule and deploy workflows that run in the environments best suited to their execution. Orchestration helps you prevent and recover from failures, and view and manage the status of workflows, making your workflow resilient, observable, and interactive. 

## The components of Orion

Designing workflows with Prefect starts with a few basic building blocks that you've already seen: flows and tasks. 

Creating and running _orchestrated_ workflows takes advantage of some additional Prefect Orion components. 

- [Orion's API server](#orion-api-server) receives state information from workflows and provides flow run instructions for executing deployments.
- [Orion's database](#orion-database) provides a persistent metadata store that holds flow and task run history.
- [Orion's UI](#orion-ui-and-dashboard) provides a control plane for monitoring, configuring, analyzing, and even creating ad-hoc runs of your Prefect workflows.
- Storage for flow and task data lets you configure a persistent store for flow code and flow and task results.
- Work queues and agents bridge the server’s orchestration environment with a your execution environments, organizing work that agents can pick up to execute.

These Orion components and services enable you to form what we call a dedicated _orchestration environment_. The same components and services enable you to orchestrate flows with either the open-source Orion API server or Prefect Cloud.

Let's take a closer look at each component.

## Orion API server

The Prefect Orion orchestration engine and API server is the central component of your orchestration environment. 

Orion's ephemeral API keeps track of the state of your Prefect flow and task runs without you having to configure or run anything other than your flow code. 

When you run an Orion API server instance, the Orion orchestration engine can run scheduled flow deployments, execute ad hoc flow runs, and lets you configure and manage work queues &mdash; on top of monitoring the state of your flows and tasks.

If your execution environment is logged into [Prefect Cloud](/ui/cloud/), Prefect's orchestration-as-a-service platform provides all the capabilities of Orion in a hosted manner.

### Running the Orion server

To take full advantage of the Orion orchestration engine and API server, you can spin up an instance at any time with the `prefect orion start` CLI command:

```bash
$ prefect orion start
Starting...

 ___ ___ ___ ___ ___ ___ _____    ___  ___ ___ ___  _  _
| _ \ _ \ __| __| __/ __|_   _|  / _ \| _ \_ _/ _ \| \| |
|  _/   / _|| _|| _| (__  | |   | (_) |   /| | (_) | .` |
|_| |_|_\___|_| |___\___| |_|    \___/|_|_\___\___/|_|\_|

Configure Prefect to communicate with the server with:

    prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api

Check out the dashboard at http://127.0.0.1:4200
```

When the Orion API server is running (either in a local environment or using Prefect Cloud), you can create and run orchestrated workflows including:

- Creating [deployments](/concepts/deployments/)
- [Scheduling](/concepts/schedules/) flow runs
- Configuring [work queues and agents](/concepts/work-queues/)
- Executing [ad hoc flow runs from deployments](/tutorials/deployments/)

During normal operation is it not expected that you will need to interact with the API directly, as this is handled automatically for you by the Python client and the [Orion UI](#the-orion-ui-and-dashboard). Most users will spin up everything all at once with `prefect orion start`.

There are numerous ways to begin exploring the API:

- Navigate to [http://127.0.0.1:4200/docs](http://127.0.0.1:4200/docs) (or your corresponding API URL) to see the autogenerated Swagger API documentation.
- Navigate to [http://127.0.0.1:4200/redoc](http://127.0.0.1:4200/redoc) (or your corresponding API URL) to see the autogenerated Redoc API documentation.
- Instantiate [an asynchronous `OrionClient`][prefect.client] within Python to send requests to the API.

To stop an instance of the Orion API server, simply **CTRL+C** to end the process in your terminal, or close the terminal session.

!!! note "Scheduled flow runs require an Orion API service"

    If you create deployments that have schedules, the scheduled flow runs will only attempt to start if the Orion API server is running. The ephemeral API does not start scheduled flow runs.

## Orion database

The Orion [database](/concepts/database/) persists data used by many features of Orion to orchestrate and track the state of your flow runs, including:

- Flow and task state
- Run history and logs
- Deployments
- Flow and task run concurrency limits
- Storage locations for flow and task results
- Work queue configuration and status

Currently Prefect supports the following databases for use as Orion's database:

- SQLite
- PostgreSQL

A local SQLite database is the default for Orion, and a local SQLite database is configured on installation. We recommend SQLite for lightweight, single-server deployments. SQLite requires essentially no setup.

PostgreSQL is good for connecting to external databases, but does require additional setup (such as Docker).

Prefect Cloud provides its own hosted database.

### Configuring the Orion database

Orion creates a SQLite database, but you can configure your own database. 

When you first install Orion, your database will be located at `~/.prefect/orion.db`. To configure this location, you can specify a connection URL with the `PREFECT_ORION_DATABASE_CONNECTION_URL` environment variable:

```bash
$ export PREFECT_ORION_DATABASE_CONNECTION_URL="sqlite+aiosqlite:////full/path/to/a/location/orion.db"
```
If at any point in your testing you'd like to reset your database, run the `prefect orion database reset` CLI command:  

```bash
$ prefect orion database reset
```

This will completely clear all data and reapply the schema.

See the [Database](/concepts/database/) documentation for further details on choosing and configuring the Orion database.

## Orion UI and dashboard

The Orion [UI and dashboard](/ui/overview/) comes prepackaged with the API when you serve it. By default it can be found at `http://127.0.0.1:4200/`:

![Prefect Orion UI dashboard.](/img/ui/orion-dashboard.png)

The dashboard allows you to track and manage your flows, runs, and deployments and additionally allows you to filter by names, tags, and other metadata to quickly find the information you are looking for.

The UI displays many useful insights about your flow runs, including:

- Flow run summaries
- Deployed flow details
- Scheduled flow runs
- Warnings for late or failed runs
- Task run details 
- Radar flow and task dependency visualizer 
- Logs

You can also use the Orion UI to create ad hoc flow runs from deployments, configure and manage work queues, and more.

See the [Orion UI & Cloud](/ui/overview/) documentation for more information about using the Orion UI.

## Storage for flow and task data

Orion lets you configure separate [storage](/concepts/storage/) to persist flow code, task results, and flow results. 

If you don't configure other storage, Orion uses temporary local storage. Temporary local storage works fine for many local flow runs, but if you run flows using Docker or Kubernetes, you must set up remote storage. 

Prefect currently supports AWS S3, Azure Blob Storage, and Google Cloud Storage.

To learn more about storage configuration, see the [Storage](/concepts/storage/) documentation. The [Running flows in Docker](/tutorials/docker-flow-runner/) and [Running flows in Kubernetes](/tutorials/kubernetes-flow-runner/) tutorials provide a brief examples of configuring remote storage.

## Work queues and agents

Work queues and agents bridge the Orion server’s orchestration environment with your local execution environments.

- Work queues are configured on the server. They contain the logic about which flows to run and how to run them. 
- Agents run in a local execution environment. They pick up work from queues and execute the flows.

There is no default global work queue or agent, so to orchestrate flow runs you need to configure at least one work queue and agent. 

You can create work queues:

- [Using ClI commands](/concepts/work-queues/#work-queue-configuration)
- [Using the Orion UI](/ui/work-queues/)

Agents are configured to pull work from a specific work queue. You'll use the CLI to [start an agent](/concepts/work-queues/#agent-configuration) in your execution environment. If you configure work queues in the Orion UI, the work queue panel provides the CLI command: you can simply copy the entire command and run it in your execution environment.

The [Deployments](/tutorials/deployments/) tutorial walks through the steps for configuring a work queue and starting an agent.

## Next steps

Continue on to the [Deployments](/tutorials/deployments/) tutorial to start seeing flow orchestration with Orion in action.