//This function updates the table with the state to use by the Pi
#r "Microsoft.WindowsAzure.Storage"
#r "Newtonsoft.Json"

using System.Net;
using Microsoft.WindowsAzure.Storage.Table;
using Newtonsoft.Json;

public static void Run(TraceWriter log, string triggerQueueItem, CloudTable serviceState, ICollector<LightStateEntity> lightTable)
{
    log.Info($"Triggered by: {triggerQueueItem}");

    TableQuery<ServiceState> rangeQuery = new TableQuery<ServiceState>().Where(
    TableQuery.GenerateFilterCondition("PartitionKey", QueryComparisons.Equal, 
            "Functions"));

    var services = serviceState.ExecuteQuerySegmented(rangeQuery, null).Results.GroupBy(x=>x.Service,(key,g)=>g.OrderBy(e=>e.Timestamp).Last());

    if(services.Any(service => service.State == "fatal"))
    {
        log.Info("Fatal service found, set lightcolor to red!");
        lightTable.Add(new LightStateEntity()
        {
            PartitionKey = "Functions",
            RowKey = Guid.NewGuid().ToString(),
            LightState = new LightState("fatal").ToJson()
        });
    }
    else if (services.Any(service => service.State == "warning"))
    {
        log.Info("Warning service found, set lightcolor to orange!");
        lightTable.Add(new LightStateEntity()
        {
            PartitionKey = "Functions",
            RowKey = Guid.NewGuid().ToString(),
            LightState = new LightState("warning").ToJson()
        });
    }
    else if (services.Any() && services.All(service => service.State == "ok"))
    {
        log.Info("Everything is Ok, set lightcolor to green!");
        lightTable.Add(new LightStateEntity()
        {
            PartitionKey = "Functions",
            RowKey = Guid.NewGuid().ToString(),
            LightState = new LightState("ok").ToJson()
        });
    }
    else
    {
        log.Info("Unknown state found, turning on all lights in blinking mode!");
        lightTable.Add(new LightStateEntity()
        {
            PartitionKey = "Functions",
            RowKey = Guid.NewGuid().ToString(),
            LightState = new LightState("error").ToJson()
        });
    }
}

public class LightStateEntity : TableEntity
{
    public string LightState { get; set; }
}

public class LightState
{
    public Light LightRed { get; set; }
    public Light LightOrange { get; set; }
    public Light LightGreen { get; set; }

    public LightState(){}

    public LightState(string state)
    {
        SetDefinedState(state);
    }

    public void SetDefinedState(string state)
    {
        switch(state)
        {
            case "fatal":
                this.LightRed = new Light(0, true);
                this.LightOrange = new Light(1, false);
                this.LightGreen = new Light(2, false);
                break;
            case "warning":
                this.LightRed = new Light(0, false);
                this.LightOrange = new Light(1, true);
                this.LightGreen = new Light(2, false);
                break;
            case "ok":
                this.LightRed = new Light(0, false);
                this.LightOrange = new Light(1, false);
                this.LightGreen = new Light(2, true);
                break;
            default:
                this.LightRed = new Light(0, true, "blink");
                this.LightOrange = new Light(1, true, "blink");
                this.LightGreen = new Light(2, true, "blink");
                break;
        }
    }

    public string ToJson()
    {
        return JsonConvert.SerializeObject(this);
    }
}

public class Light
{
    public int Number { get; set; }
    public string Color { get; set; }
    public bool On { get; set; }
    public string Pattern { get; set; }

    public Light(int number, bool on, string pattern = "solid")
    {
        switch(number)
        {
            case 0:
                this.Number = number;
                this.Color = "red";
                this.On = on;
                this.Pattern = pattern;
                break;
            case 1:
                this.Number = number;
                this.Color = "orange";
                this.On = on;
                this.Pattern = pattern;
                break;
            case 2:
                this.Number = number;
                this.Color = "green";
                this.On = on;
                this.Pattern = pattern;
                break;
        }
    }
}

public class ServiceState : TableEntity
{
    public string Service { get; set; }
    public string State { get; set; }
}