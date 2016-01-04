<form id="samplesForm">
<div id="samples_summary" class="summary span-24 last">
  <h2><strong>Samples matching <?= $match ?></strong></h2>
</div>

<table id="samples" class="display">
  <thead>
    <tr>
      <th>Sample name</th>
      <th>Run</th>
      <th>Annotations (<a class="showAll" href="#">show all</a>, <a class="hideAll" href="#">hide all</a>)</th>
    </tr>
  </thead>
    
  <tbody>
<?php
foreach ($samples as $sample) {
?>
    <tr>
      <td><?= $sample->sample_name ?></td>
      <td><a href="<?= url_for('runs', $sample->run_accession); ?>"><?= format_run_accession($sample->run_accession) ?></a></td>
      <td><div class="metadata toggle">
        <em>In core sample registry:</em>
        <ul>
          <li><strong>Accession</strong>:<?= format_sample_accession($sample->sample_accession) ?></li>
          <li><strong>Barcode</strong>:<?= strtoupper($sample->barcode_sequence) ?></li>
          <li><strong>Primer</strong>:<?= strtoupper($sample->primer_sequence) ?></li>
        </ul>
<?php
if (array_key_exists($sample->sample_accession, $sample_metadata)) {
    $metadata_by_file = $sample_metadata[$sample->sample_accession];
} else {
    $metadata_by_file = array();
}
foreach ($metadata_by_file as $fp => $tags) { 
?>
        <em>In <?= $fp ?>:</em>
        <ul>
<?php
foreach ($tags as $tag) {
?>
          <li><strong><?= $tag->key ?></strong>:<?= $tag->val ?></li>
<?php
} // tag
?>
        </ul>
<?php
} // file
?>
      </div></td>
    </tr>
<?php
} // sample
?>
  </tbody>
</table>
</form>

<script type="text/javascript">
$(document).ready(function () {
    /* Set up data table */
    $('#samples').dataTable({
        "bSort": false,
        "bPaginate": false,
    });

    /* Move search box to bottom of summary area */
    $("#samples_filter").appendTo('#samples_summary');

    /* Toggle detailed sample metadata */
    $('.toggle').each(function() {
        var nItems = $(this).find('li').length;
        if (nItems > 0) {
            var toggleText = nItems + ' annotations';
    	    $(this).parent().prepend(
    	        '<a href="#" class="toggleLink">' + toggleText + '</a>');
            } else {
    	        $(this).parent().prepend('None');
    	    }
        $(this).hide();
    });

    $('a.toggleLink').click(function() {
        $(this).next().toggle();
        return false; // do not follow link
    });

    $('a.showAll').click(function() {
        $('.toggle').show();
        return false;
    });

    $('a.hideAll').click(function() {
        $('.toggle').hide();
        return false;
    });
});
</script>

