<form id="samplesForm">
<div id="samples_summary" class="summary span-24 last">
  <h2><strong>Samples tagged with <?= $tag ?> = <?= $value ?></strong></h2>
</div>

<table id="samples" class="display">
  <thead>
    <tr>
      <th>Sample name</th>
      <th>Primer</th>
      <th>Run date</th>
      <th>Run accession</th>
      <th>Annotations (<a class="showAll" href="#">show all</a>, <a class="hideAll" href="#">hide all</a>)</th>
    </tr>
  </thead>
  <tbody>
<?php
foreach ($samples as $sample) {
?>
    <tr>
      <td><?= $sample->sample_name ?></td>
                          <td><?= strtoupper($sample->primer_sequence) ?></td>
      <td><span class="date"><?= format_date($sample->run_date) ?></span></td>
      <td><a href="<?= url_for('runs', $sample->run_accession); ?>"><?= format_run_accession($sample->run_accession) ?></a></td>
      <td><div class="metadata toggle">
        <ul>
          <li><strong>sample_accession</strong>:<?= format_sample_accession($sample->sample_accession) ?></li>
<?php
if (array_key_exists($sample->sample_accession, $sample_metadata)) {
    $annotations = $sample_metadata[$sample->sample_accession];
} else {
    $annotations = array();
}
foreach ($annotations as $a) { 
?>
          <li><strong><?= $a->key ?></strong>:<?= $a->val ?></li>
<?php
} // tag
?>
        </ul>
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
	    $(this).parent().prepend('<a href="#" class="toggleLink">' + toggleText + '</a>');
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

