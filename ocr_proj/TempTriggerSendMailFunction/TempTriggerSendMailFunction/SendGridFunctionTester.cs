using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.Extensions.Logging;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace TempTriggerSendMailFunction
{
    public static class SendGridFunctionTester
    {
        [FunctionName("SendGridFunctionTester")]
        public static async Task<IActionResult> Run(
            [HttpTrigger(AuthorizationLevel.Function, "get", Route = null)] HttpRequest req,
            ILogger log)
        {
            log.LogInformation("C# HTTP trigger function processed a request.");

            var jsonData = JsonSerializer.Serialize(new
            {
                email = "maciekkoz98@gmail.com",
                code = "asdasdasd"
            });

            var httpClient = new HttpClient();
            var url = "https://prod-145.westeurope.logic.azure.com:443/workflows/ebdbfc4977234440b9a48a98a9fa36af/triggers/manual/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=1wlap-WyQ-Qi9WYsFRliBWAdXCSPg9aljr7LupDnHsI";
            var content = new StringContent(jsonData, Encoding.UTF8, "application/json");
            var result = await httpClient.PostAsync(url, content);

            return new OkObjectResult(result);
        }
    }
}
