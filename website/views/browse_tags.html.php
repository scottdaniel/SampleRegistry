<div class="summary span-24 last">

<h2>Sample annotations</h2>

<p>Click on a sample annotation to see a table of annotation values, broken 
down by sequencing run.</p>

<h3>Standard annotations</h3>
<p class="standardtags">
	<a href="<?= url_for('tags', 'SampleType') ?>">SampleType</a>
	<a href="<?= url_for('tags', 'HostSpecies') ?>">HostSpecies</a>
	<a href="<?= url_for('tags', 'SubjectID') ?>">SubjectID</a>
</p>

<h3>Other sample annotations</h3>

<p class="tagcloud">
<?php 
foreach ($tags as $tag) {
?>
	<a href="<?= url_for('tags', $tag->key) ?>" style="font-size: <?= 10 + 90 * ($tag->key_counts / $maxcnt) ?>px"><?= $tag->key ?></a> 
<?php
}
?>
</p>
</div>
