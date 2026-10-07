using Microsoft.EntityFrameworkCore;
using PropMate.Api.Data;
using PropMate.Api.DTOs.Transactions;
using PropMate.Api.Enums;
using PropMate.Api.Models;
using PropMate.Api.Services;

namespace PropMate.Api.Tests;

public class TransactionServiceTests
{
    private static AppDbContext CreateContext()
    {
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;

        return new AppDbContext(options);
    }

    private static PropertyListing CreateSaleListing(
        ListingStatus status,
        int ownerId = 100)
    {
        return new PropertyListing
        {
            OwnerId = ownerId,
            Title = "House for Sale in Colombo",
            Description =
                "A spacious property created for transaction service testing.",
            Purpose = ListingPurpose.Sale,
            PropertyType = PropertyType.House,
            Price = 25000000,
            Address = "100 Test Road",
            City = "Colombo",
            Bedrooms = 4,
            Bathrooms = 3,
            Status = status
        };
    }

    private static CreatePurchaseOfferDto CreateOffer(int listingId)
    {
        return new CreatePurchaseOfferDto
        {
            PropertyListingId = listingId,
            OfferAmount = 24000000,
            Conditions = "Subject to final inspection."
        };
    }

    [Fact]
    public async Task CreatePurchaseOffer_DraftListing_ShouldThrowException()
    {
        await using var context = CreateContext();

        var listing = CreateSaleListing(ListingStatus.Draft);
        context.PropertyListings.Add(listing);
        await context.SaveChangesAsync();

        var service = new TransactionService(context);

        var exception =
            await Assert.ThrowsAsync<InvalidOperationException>(
                () => service.CreatePurchaseOfferAsync(
                    buyerId: 200,
                    CreateOffer(listing.Id)));

        Assert.Contains(
            "published sale listings",
            exception.Message);
    }

    [Fact]
    public async Task CreatePurchaseOffer_ByListingOwner_ShouldThrowException()
    {
        await using var context = CreateContext();

        var listing = CreateSaleListing(
            ListingStatus.Published,
            ownerId: 100);

        context.PropertyListings.Add(listing);
        await context.SaveChangesAsync();

        var service = new TransactionService(context);

        var exception =
            await Assert.ThrowsAsync<InvalidOperationException>(
                () => service.CreatePurchaseOfferAsync(
                    buyerId: 100,
                    CreateOffer(listing.Id)));

        Assert.Contains(
            "Owners cannot submit purchase offers",
            exception.Message);
    }

    [Fact]
public async Task CreatePurchaseOffer_ValidPublishedSale_ShouldCreateOffer()
{
    await using var context = CreateContext();

    var buyer = new User
    {
        Id = 200,
        FirstName = "Test",
        LastName = "Buyer",
        Email = "buyer@test.local",
        PasswordHash = "test-hash",
        Role = UserRole.BuyerRenter
    };

    var listing = CreateSaleListing(
        ListingStatus.Published,
        ownerId: 100);

    context.Users.Add(buyer);
    context.PropertyListings.Add(listing);
    await context.SaveChangesAsync();

    var service = new TransactionService(context);

    var result = await service.CreatePurchaseOfferAsync(
        buyerId: buyer.Id,
        CreateOffer(listing.Id));

    Assert.NotNull(result);
    Assert.Equal(listing.Id, result.PropertyListingId);
    Assert.Equal(buyer.Id, result.BuyerId);
    Assert.Equal(24000000m, result.OfferAmount);

    Assert.Single(context.PurchaseOffers);
}
}