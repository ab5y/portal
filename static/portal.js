function goToTab(tab, isInvisible) {
	// Deactivate currently active tab
	$('.mdl-tabs__tab.is-active').removeClass('is-active');
	// Deactivate currentyl active panel
	$('.mdl-tabs__panel.is-active').removeClass('is-active');
	// Activate desired tab
	var tabId = '#'+tab+'-tab';
	$(tabId).addClass('is-active');
	// If invisible, make visible
	if(isInvisible)
		$(tabId).removeClass('invisible');
	// Activate desired panel
	var panelId = '#'+tab+'-panel';
	$(panelId).addClass('is-active');
}