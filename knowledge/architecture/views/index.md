# Views

Diagram-first concepts that answer one question each. Names follow [C4 System Views](/architecture/c4-system-views.md).

* [Deployment View](deployment-view.md) - Where Vyasa's processes, files, and external systems live on a developer machine.
* [Scan Pipeline Views](scan-pipeline-views.md) - Component, dynamic, and decision views of workspace discovery, inspection, detection, and incremental reuse.
* [Data Model Views](data-model-views.md) - Entity relationships at table level, and the state machines of identity, availability, value status, and runs.
* [MCP Views](mcp-views.md) - Components of the MCP adapter, and the success and failure paths of one tool call.
* [Storage Views](storage-views.md) - How the index database opens and migrates, how a scan writes safely, and how recovery chooses between restore and rebuild.
* [Synchronization Views](sync-views.md) - The registry context, one synchronization run, and how a field conflict is decided.
* [Remote Discovery Views](remote-views.md) - The provider boundary, a discovery run with pagination and failure, remote access states, and reconciliation with local data.
* [Security Views](security-views.md) - Trust zones and what may cross them, and how each documented threat is met by a control.
