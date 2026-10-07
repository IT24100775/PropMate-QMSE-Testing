using System.Security.Claims;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using PropMate.Api.Controllers;
using PropMate.Api.Data;
using PropMate.Api.Enums;
using PropMate.Api.Models;

namespace PropMate.Api.Tests;

public class ViewingBookingsControllerTests
{
    private static AppDbContext CreateContext()
    {
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;

        return new AppDbContext(options);
    }

    private static ViewingBookingsController CreateController(
        AppDbContext context,
        int userId = 200)
    {
        var controller = new ViewingBookingsController(context);

        var claims = new[]
        {
            new Claim(
                ClaimTypes.NameIdentifier,
                userId.ToString())
        };

        var identity = new ClaimsIdentity(
            claims,
            "TestAuthentication");

        var principal = new ClaimsPrincipal(identity);

        controller.ControllerContext = new ControllerContext
        {
            HttpContext = new DefaultHttpContext
            {
                User = principal
            }
        };

        return controller;
    }

    private static PropertyListing CreateListing(
        ListingStatus status)
    {
        return new PropertyListing
        {
            OwnerId = 100,
            Title = "Viewing Test Apartment",
            Description =
                "A property listing created for viewing booking controller tests.",
            Purpose = ListingPurpose.Rent,
            PropertyType = PropertyType.Apartment,
            Price = 150000,
            Address = "123 Test Road",
            City = "Colombo",
            Bedrooms = 3,
            Bathrooms = 2,
            Status = status
        };
    }

    [Fact]
    public async Task BookViewing_NonExistentSlot_ShouldReturnNotFound()
    {
        await using var context = CreateContext();

        var controller = CreateController(context);

        var request = new CreateViewingBookingRequest
        {
            ViewingSlotId = 999
        };

        var result = await controller.BookViewing(request);

        Assert.IsType<NotFoundObjectResult>(result);
    }

    [Fact]
    public async Task BookViewing_NonPublishedProperty_ShouldReturnNotFound()
    {
        await using var context = CreateContext();

        var listing = CreateListing(ListingStatus.Draft);

        var slot = new ViewingSlot
        {
            PropertyListing = listing,
            StartTime = DateTime.UtcNow.AddDays(1),
            EndTime = DateTime.UtcNow.AddDays(1).AddHours(1),
            IsAvailable = true
        };

        context.ViewingSlots.Add(slot);
        await context.SaveChangesAsync();

        var controller = CreateController(context);

        var request = new CreateViewingBookingRequest
        {
            ViewingSlotId = slot.Id
        };

        var result = await controller.BookViewing(request);

        Assert.IsType<NotFoundObjectResult>(result);
    }

    [Fact]
    public async Task BookViewing_UnavailableSlot_ShouldReturnConflict()
    {
        await using var context = CreateContext();

        var listing = CreateListing(ListingStatus.Published);

        var slot = new ViewingSlot
        {
            PropertyListing = listing,
            StartTime = DateTime.UtcNow.AddDays(1),
            EndTime = DateTime.UtcNow.AddDays(1).AddHours(1),
            IsAvailable = false
        };

        context.ViewingSlots.Add(slot);
        await context.SaveChangesAsync();

        var controller = CreateController(context);

        var request = new CreateViewingBookingRequest
        {
            ViewingSlotId = slot.Id
        };

        var result = await controller.BookViewing(request);

        Assert.IsType<ConflictObjectResult>(result);
    }
}