# Mermaid Chart Comparison

## Flowchart

```mermaid
flowchart LR
	request[Submit request] --> review[Review request]
	review --> reply[Reply to customer]
	reply --> receive[Receive reply]
```

## Swimlane

```mermaid
swimlane-beta LR
	subgraph Customer
		request[Submit request]
		receive[Receive reply]
	end

	subgraph Support
		review[Review request]
		reply[Reply to customer]
	end

	request --> review --> reply --> receive
```
