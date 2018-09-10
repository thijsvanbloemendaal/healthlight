//This function returns the light status to the Pi on a GET request
#r "Microsoft.WindowsAzure.Storage"
#r "Newtonsoft.Json"

using System.Net;
using Microsoft.WindowsAzure.Storage.Table;
using Newtonsoft.Json;

public static HttpResponseMessage Run(HttpRequestMessage req, CloudTable lightTable, TraceWriter log)
{
    //Log the request IP
    IEnumerable<string> values;
    if (req.Headers.TryGetValues("IP", out values))
    {
        log.Info("IP: " + values.FirstOrDefault().Split(new char[] { ',' }).FirstOrDefault().Split(new char[] { ':' }).FirstOrDefault());
    }

    TableQuery<LightStateEntity> rangeQuery = new TableQuery<LightStateEntity>().Where(
    TableQuery.GenerateFilterCondition("PartitionKey", QueryComparisons.Equal, 
            "Functions"));

    var light = lightTable.ExecuteQuerySegmented(rangeQuery, null).Results.OrderByDescending(r => r.Timestamp).FirstOrDefault();
    log.Info(light.LightState);
    return req.CreateResponse(HttpStatusCode.OK, JsonConvert.DeserializeObject(light.LightState));
}

public class LightStateEntity : TableEntity
{
    public string LightState { get; set; }
}
