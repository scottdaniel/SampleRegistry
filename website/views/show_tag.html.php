<div class="summary" id="tag_summary">
  <h2>Sample metadata tag: <em><?= $tag ?></em></h2>
</div>

<table id="tagstats" class="display">
  <thead>
    <tr>
      <th>Value</th>
      <th>Number of samples</th>
      <th>Run</th>
      <th>Run date</th>
      <th>Run Comment</th>
    </tr>
  </thead>
  <tbody>
<?php
foreach ($stats as $stat) {
?>
    <tr>
      <td><a href="<?= url_for('tags', $tag, $stat->val); ?>"><?= $stat->val ?></a></td>
      <td><?= $stat->sample_count ?></td>
      <td><a href="<?= url_for('runs', $stat->run_accession); ?>"><?= format_run_accession($stat->run_accession) ?></a></td>
      <td><?= format_date($stat->run_date) ?></td>
      <td><?= $stat->run_comment ?></td>
    </tr>
<?php
} // stat
?>
  </tbody>
</table>

<script type="text/javascript">
$(document).ready(function () {
    /* Set up data table */
    $('#tagstats').dataTable({
        "bPaginate": false,
    });

    /* Move search box to bottom of summary area */
    $("#tagstats_filter").appendTo('#tag_summary');
});
</script>


