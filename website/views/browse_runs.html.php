<div id="runs_summary" class="summary span-24 last">
  <h2>Sequencing runs</h2>
  <p>Each output file from a sequencing run is given a unique accession number
  (shown on left).  Runs can be filtered using the search box below.</p>
</div>

<table class="display" id="runs">
  <thead>
    <tr>
      <th>&nbsp;</th>
      <th>Date</th>
      <th>Platform</th>
      <th>Lane</th>
      <th>Samples</th>
      <th>Comment</th>
    </tr>
  </thead>
  <tbody>
<?php
foreach ($runs as $run) {
    if (preg_match("/^Illumina/", $run->machine_type)) {
        $platform = "Illumina";
    } else {
        $platform = $run->machine_type;
    }
    $platform .= '&nbsp;' . $run->machine_kit;
?>
    <tr>
      <td><a href="<?= url_for('runs', $run->run_accession) ?>"><?= format_run_accession($run->run_accession) ?></a></td>
      <td><span class="date"><?= format_date($run->run_date) ?></span></td>
      <td><nobr><?= $platform ?></nobr></td>
      <td><?= $run->lane ?></td>
      <td><?= $run->sample_count ?></td>
      <td><?= $run->comment ?></td>
    </tr>
<?php
} // runs
?>
  </tbody>
</table>

<script type="text/javascript">
$(document).ready(function () {
    /* Initialize the DataTable */
    oTable = $('#runs').dataTable({
        "bSort": false,
        "iDisplayLength": 20,
        "bLengthChange": false,
        "sPaginationType": "full_numbers",
        "bStateSave": true,
    });

    /* Move search box to bottom of summary area */
    $("#runs_filter").appendTo('#runs_summary');

    /* Snap pagination info to grid */
    $("#runs_info").addClass("span-12");
    $("#runs_paginate").addClass("span-12 last")

    /* Moving the search box breaks the state saving routine */
    /* Redraw manually */
    oTable.fnDraw();
});
</script>
