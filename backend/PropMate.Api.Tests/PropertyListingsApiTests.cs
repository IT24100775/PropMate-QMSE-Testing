using System.IdentityModel.Tokens.Jwt;
using System.Net;
using System.Net.Http.Headers;
using System.Security.Claims;
using System.Text;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.IdentityModel.Tokens;

namespace PropMate.Api.Tests;

public class PropertyListingsApiTests
{
    private const string JwtKey =
        "ThisIsATestJwtKeyThatIsLongEnoughForTesting123456";

    private const string JwtIssuer = "PropMate.Tests";
    private const string JwtAudience = "PropMate.Tests";

    private static WebApplicationFactory<Program> CreateFactory()
    {
        Environment.SetEnvironmentVariable("Jwt__Key", JwtKey);
        Environment.SetEnvironmentVariable("Jwt__Issuer", JwtIssuer);
        Environment.SetEnvironmentVariable("Jwt__Audience", JwtAudience);

        Environment.SetEnvironmentVariable(
            "PropertyVerificationService__BaseUrl",
            "http://localhost:8001");

        Environment.SetEnvironmentVariable(
            "AgenticAiService__BaseUrl",
            "http://localhost:8002");

        Environment.SetEnvironmentVariable(
            "PropertyManager__Email",
            null);

        Environment.SetEnvironmentVariable(
            "PropertyManager__Password",
            null);

        return new WebApplicationFactory<Program>()
            .WithWebHostBuilder(builder =>
            {
                builder.UseSetting("Environment", "Testing");
            });
    }

    private static string CreateTestToken(
        int userId,
        string email,
        string role)
    {
        var claims = new[]
        {
            new Claim(
                ClaimTypes.NameIdentifier,
                userId.ToString()),

            new Claim(
                ClaimTypes.Email,
                email),

            new Claim(
                ClaimTypes.Role,
                role)
        };

        var key = new SymmetricSecurityKey(
            Encoding.UTF8.GetBytes(JwtKey));

        var credentials = new SigningCredentials(
            key,
            SecurityAlgorithms.HmacSha256);

        var token = new JwtSecurityToken(
            issuer: JwtIssuer,
            audience: JwtAudience,
            claims: claims,
            expires: DateTime.UtcNow.AddMinutes(30),
            signingCredentials: credentials);

        return new JwtSecurityTokenHandler()
            .WriteToken(token);
    }

    private static void Authenticate(
        HttpClient client,
        string role)
    {
        var token = CreateTestToken(
            999,
            "test@propmate.local",
            role);

        client.DefaultRequestHeaders.Authorization =
            new AuthenticationHeaderValue(
                "Bearer",
                token);
    }

    [Fact]
    public async Task HealthEndpoint_ShouldReturnSuccess()
    {
        using var factory = CreateFactory();
        using var client = factory.CreateClient();

        var response = await client.GetAsync("/health");

        Assert.Equal(
            HttpStatusCode.OK,
            response.StatusCode);
    }

    [Fact]
    public async Task OwnerListings_WithoutAuthentication_ShouldReturnUnauthorized()
    {
        using var factory = CreateFactory();
        using var client = factory.CreateClient();

        var response = await client.GetAsync(
            "/api/propertylistings/owner");

        Assert.Equal(
            HttpStatusCode.Unauthorized,
            response.StatusCode);
    }

    [Fact]
    public async Task AdminListings_WithoutAuthentication_ShouldReturnUnauthorized()
    {
        using var factory = CreateFactory();
        using var client = factory.CreateClient();

        var response = await client.GetAsync(
            "/api/propertylistings/admin");

        Assert.Equal(
            HttpStatusCode.Unauthorized,
            response.StatusCode);
    }

    [Fact]
    public async Task AdminListings_AsOwnerAgent_ShouldReturnForbidden()
    {
        using var factory = CreateFactory();
        using var client = factory.CreateClient();

        Authenticate(client, "OwnerAgent");

        var response = await client.GetAsync(
            "/api/propertylistings/admin");

        Assert.Equal(
            HttpStatusCode.Forbidden,
            response.StatusCode);
    }

    [Fact]
    public async Task OwnerListings_AsBuyerRenter_ShouldReturnForbidden()
    {
        using var factory = CreateFactory();
        using var client = factory.CreateClient();

        Authenticate(client, "BuyerRenter");

        var response = await client.GetAsync(
            "/api/propertylistings/owner");

        Assert.Equal(
            HttpStatusCode.Forbidden,
            response.StatusCode);
    }
}