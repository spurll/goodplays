function toggleFilters() {
  $("#filters").slideToggle("normal", setFilterName);
}

function setFilterName() {
  if ($("#filters").is(":visible")) {
    $(".toggle-filters").html("Less &and;");
  }
  else {
    $(".toggle-filters").html("More &or;");
  }
}

$(document).ready(() => setFilterName());
