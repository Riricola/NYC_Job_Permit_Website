
function sortTable(n) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("myTable");
    switching = true;
    dir = "asc"; // Set the default sorting direction to ascending

    while (switching) {
        switching = false;
        rows = table.rows;

        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("TD")[n];
            y = rows[i + 1].getElementsByTagName("TD")[n];

            // Compare the two date values
            let xDate = new Date(x.innerHTML);
            let yDate = new Date(y.innerHTML);

            if (dir == "asc") {
                if (xDate > yDate) {
                    shouldSwitch = true;
                    break;
                }
            } else if (dir == "desc") {
                if (xDate < yDate) {
                    shouldSwitch = true;
                    break;
                }
            }
        }

        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            switchcount++;
        } else {
            if (switchcount == 0 && dir == "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
}

// Automatically sort by the Filing Date column (column index 6) on page load
window.onload = function () {
    sortTable(9);
};
