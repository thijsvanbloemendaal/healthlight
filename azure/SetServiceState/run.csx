//This function saves the service state delivered by the post action
#r "Microsoft.WindowsAzure.Storage"

using System.Net;
using Microsoft.WindowsAzure.Storage.Table;

public static async Task<HttpResponseMessage> Run(HttpRequestMessage req, ICollector<ServiceState> serviceStateTable, ICollector<string> triggerQueueItem, TraceWriter log)
{
    dynamic data = await req.Content.ReadAsAsync<object>();
    string service = data?.service;
    string state = data?.state;

    if (service == null)
    {
        return req.CreateResponse(HttpStatusCode.BadRequest, "Please pass a servicename in the request body");
    }
    if (state == null)
    {
        return req.CreateResponse(HttpStatusCode.BadRequest, "Please pass a state of the service in the request body");
    }

    SetServiceState(serviceStateTable, service, state);

    triggerQueueItem.Add("Service triggered UpdateLightState: " + service); 

    return req.CreateResponse(HttpStatusCode.Created);
}

public static void SetServiceState(ICollector<ServiceState> serviceStateTable, string service, string state)
{
    serviceStateTable.Add(new ServiceState()
    {
        PartitionKey = "Functions",
        RowKey = Guid.NewGuid().ToString(),
        Service = service,
        State = state
    });
}

public class ServiceState : TableEntity
{
    public string Service { get; set; }
    public string State { get; set; }
}