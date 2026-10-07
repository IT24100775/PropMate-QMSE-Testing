using Microsoft.EntityFrameworkCore;
using PropMate.Api.Data;
using PropMate.Api.DTOs.Maintenance;
using PropMate.Api.Models.Maintenance;
using PropMate.Api.Services.Maintenance;

namespace PropMate.Api.Tests;

public class MaintenanceServiceTests
{
    private static ApplicationDbContext CreateContext()
    {
        var options = new DbContextOptionsBuilder<ApplicationDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;

        return new ApplicationDbContext(options);
    }

    private static MaintenanceRequest CreatePendingRequest()
    {
        return new MaintenanceRequest
        {
            PropertyId = 1,
            TenantId = 10,
            Description = "Water leak in kitchen",
            Category = "Plumbing",
            Priority = "HIGH",
            Status = "PENDING",
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };
    }

    [Fact]
    public async Task UpdateStatus_PendingToAssigned_ShouldSucceed()
    {
        await using var context = CreateContext();

        var request = CreatePendingRequest();
        context.MaintenanceRequests.Add(request);
        await context.SaveChangesAsync();

        var service = new MaintenanceService(context);

        var dto = new UpdateMaintenanceStatusDto
        {
            Status = "ASSIGNED",
            ChangedBy = 100,
            Comment = "Technician assigned."
        };

        var result = await service.UpdateStatusAsync(request.Id, dto);

        Assert.NotNull(result);
        Assert.Equal("ASSIGNED", result.Status);
    }

    [Fact]
    public async Task UpdateStatus_PendingToResolved_ShouldThrowException()
    {
        await using var context = CreateContext();

        var request = CreatePendingRequest();
        context.MaintenanceRequests.Add(request);
        await context.SaveChangesAsync();

        var service = new MaintenanceService(context);

        var dto = new UpdateMaintenanceStatusDto
        {
            Status = "RESOLVED",
            ChangedBy = 100,
            Comment = "Invalid direct resolution attempt."
        };

        var exception = await Assert.ThrowsAsync<Exception>(
            () => service.UpdateStatusAsync(request.Id, dto));

        Assert.Contains(
            "Cannot change status from 'PENDING' to 'RESOLVED'",
            exception.Message);
    }

    [Fact]
    public async Task UpdateStatus_ValidTransition_ShouldCreateHistory()
    {
        await using var context = CreateContext();

        var request = CreatePendingRequest();
        context.MaintenanceRequests.Add(request);
        await context.SaveChangesAsync();

        var service = new MaintenanceService(context);

        var dto = new UpdateMaintenanceStatusDto
        {
            Status = "ASSIGNED",
            ChangedBy = 100,
            Comment = "Valid workflow transition."
        };

        await service.UpdateStatusAsync(request.Id, dto);

        var history = await context.MaintenanceStatusHistories
            .SingleAsync();

        Assert.Equal(request.Id, history.MaintenanceRequestId);
        Assert.Equal("PENDING", history.OldStatus);
        Assert.Equal("ASSIGNED", history.NewStatus);
        Assert.Equal(100, history.ChangedBy);
    }
}