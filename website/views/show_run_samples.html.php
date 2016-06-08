<form id="samplesForm">
<div id="samples_summary" class="summary span-24 last">
  <h2>
    <strong>Run <?= format_run_accession($run->run_accession) ?></strong><br/>
    <em><?= $run->comment ?></em>
  </h2>
  <ul>
    <li><strong>Date:</strong> <?= format_date($run->run_date) ?></li>
    <li><strong>Lane:</strong> <?= $run->lane ?></li>
    <li><strong>Platform:</strong> <?= $run->machine_type ?> <?= $run->machine_kit ?></li>
    <li><strong>Data file:</strong> <a href="respublica.research.chop.edu:/mnt/isilon/microbiome/<?= $run->data_uri ?>"><?= basename($run->data_uri) ?></a></li>
  </ul>
  <p>
    <strong>Export metadata for all samples:</strong><br />
    <a href="<?= url_for('runs', $run->run_accession . ".txt"); ?>">QIIME-compatible mapping file</a><br/>
    <a href="<?= url_for('runs', $run->run_accession . ".tsv"); ?>">Tab-delimited format (compatible with <code>read.delim</code> function in R)</a>
  </p>
</div>

<table id="samples" class="display">
  <thead>
    <tr>
      <th>Sample name</th>
      <th>Barcode</th>
      <th>Primer</th>
      <th>Annotations (<a class="showAll" href="#">show all</a>, <a class="hideAll" href="#">hide all</a>)</th>
    </tr>
  </thead>
  <tbody>
<?php
foreach ($samples as $sample) {
?>
    <tr>
      <td><?= $sample->sample_name ?></td>
      <td><?= strtoupper($sample->barcode_sequence) ?></td>
      <td><?= strtoupper($sample->primer_sequence) ?></td>
      <td><div class="metadata toggle">
        <ul>
          <li><strong>sample_accession</strong>:<?= format_sample_accession($sample->sample_accession) ?></li>
          <li><strong>SampleType</strong>:<?= $sample->sample_type ? $sample->sample_type : "NA" ?></li>
          <li><strong>HostSpecies</strong>:<?= $sample->host_species ? $sample->host_species : "NA" ?></li>
          <li><strong>SubjectID</strong>:<?= $sample->subject_id ? $sample->subject_id : "NA" ?></li>
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

