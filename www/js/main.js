
var searchResults = [];
var selectedResult = null;
var externalIdType = null;
var externalId = null;

function amazonLookup(source, idType) {
    var itemId = source.val();

    if (idType == 'upc' && itemId.length == 13)
        idType = 'ean';

    var url = 'rpc';
    var request = {};
    request.method = 'amazon_lookup';
    request.params = {};
    request.params.id_type = idType;
    request.params[idType] = itemId;
    request.id = 1;
    request.jsonrpc = '2.0';

    searchResults = [];
    selectedResult = null;
    var obj = source.parent();
    obj.find('span.glyphicon').removeClass('glyphicon-remove').removeClass('glyphicon-ok');
    obj.removeClass('has-success').removeClass('has-error');
    updateResults();
    updateSelected();

    externalIdType = idType;
    externalId = itemId;

    $.post(url, JSON.stringify(request), function (response) {
        result = response.result;
        if (result !== false)
            result = [result];
        handleSearchResponse(result, source.parent());
    }, 'json');
}

function amazonSearch() {
    var source = $('#keywords');
    var itemId = source.val();
    var url = 'rpc';
    var request = {};
    request.method = 'amazon_search';
    request.params = [itemId];
    request.id = 1;
    request.jsonrpc = '2.0';

    searchResults = [];
    selectedResult = null;
    var obj = source.parent();
    obj.find('span.glyphicon').removeClass('glyphicon-remove').removeClass('glyphicon-ok');
    obj.removeClass('has-success').removeClass('has-error');
    updateResults();
    updateSelected();

    externalIdType = externalId = null;

    $.post(url, JSON.stringify(request), function (response) {
        result = response.result;
        handleSearchResponse(result, source.parent());
    }, 'json');
}

function requestResultImage(asin) {
    var url = 'rpc';
    var request = {};
    request.method = 'amazon_get_image';
    request.params = [asin];
    request.id = 1;
    request.jsonrpc = '2.0';

    $.post(url, JSON.stringify(request), function (response) {
        result = response.result;
        if (result !== false)
            $('#result-image').html('<img src="' + result + '" />')
    }, 'json');
}

function handleSearchResponse(results, sourceGroup) {
    if ((results === false) || (results.length <= 0)) {
        sourceGroup.find('span.glyphicon').addClass('glyphicon-remove');
        sourceGroup.addClass('has-error');
    } else {
        searchResults = results;
        sourceGroup.find('span.glyphicon').addClass('glyphicon-ok');
        sourceGroup.addClass('has-success');
        updateResults();
        $('#results option')[0].selected = true;
        updateSelected();
    }
}

function updateResults() {
    var output = [];
    $.each(searchResults, function(index, value) {
        var key = value.asin;
        var desc = value.title + ' (' + value.group + ' ' + value.asin + ')';

        output.push('<option value="'+ key +'">'+ desc +'</option>');
    });

    $('#results').html(output.join(''));
}

function updateSelected(itemId, itemDesc) {
    var asin = $('#results').val();
    if (asin === null) {
        $('#results-group').hide();
        selectedResult = null;
    } else {
        $('#results-group').show();
        selectedResult = asin;

        // Find the appropriate result entry
        for (var i = 0; i < searchResults.length; i++) {
            thisResult = searchResults[i];
            if (thisResult.asin != asin)
                continue;

            $('#result-image').html('');
            requestResultImage(asin);
            newHtml = '<ul>\n';
            for (var key in searchResults[i]) {
                newHtml += '\t<li><b>' + key + '</b>: ' + searchResults[i][key] + '</li>\n'
            }
            newHtml += '</ul>\n';
            $('#selected-result').html(newHtml);
            break;
        }
    }
}

function autoSaveIfAppropriate() {
    if (selectedResult === null)
        return
    if (!$('#autosave').is(":checked"))
        return
    addSelectedToCatalog();
}

function addSelectedToCatalog() {
    var url = 'rpc';
    var request = {};
    request.method = 'amazon_add_item';
    request.params = {};
    request.params.asin = selectedResult;
    if (externalIdType !== null)
        request.params[externalIdType] = externalId;
    request.id = 1;
    request.jsonrpc = '2.0';

    $.post(url, JSON.stringify(request), function (response) {
        result = response.result;
        if (result === false) {
            toastr.success("Successfully added item to catalog", "Item Added");
        } else {
            toastr.warning("The item was not added. Reason: " + result, "Item Not Added");
        }
    }, 'json').fail(function () {
        toastr.error("A server error occurred", "Item Not Added");
    });
}

// Set up event handlers

$(document).ready(function() {
    $('#results-group').hide();

    // UPC/EAN enter key
    $('#upc').keypress(function (e) {
        if (e.which == 13) {
            autoSaveIfAppropriate();
            amazonLookup($(this), 'upc');
            $(this).select();
            return false;
        }
    });

    // ISBN enter key
    $('#isbn').keypress(function (e) {
        if (e.which == 13) {
            autoSaveIfAppropriate();
            amazonLookup($(this), 'isbn');
            $(this).select();
            return false;
        }
    });

    // ASIN enter key
    $('#asin').keypress(function (e) {
        if (e.which == 13) {
            autoSaveIfAppropriate();
            amazonLookup($(this), 'asin');
            $(this).select();
            return false;
        }
    });

    // Keywords enter key
    $('#keywords').keypress(function (e) {
        if (e.which == 13) {
            autoSaveIfAppropriate();
            amazonSearch($(this));
            $(this).select();
            return false;
        }
    });

    // User selection of search result, or automatic selection of the first result
    $('#results').change(updateSelected);

    // Add item to catalog
    $('#add-to-catalog').click(addSelectedToCatalog);
});