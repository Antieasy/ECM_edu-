let title = document.querySelector('title');
let topMenuLinks = document.getElementsByClassName('nav-item');
let titleText = title.textContent.replaceAll('\n', '');
titleText = titleText.replaceAll('\t', '');
titleText = titleText.replaceAll(' ', '');
let tempMenuLinkText;
for (let i = 0; i < topMenuLinks.length; i++) {
	tempMenuLinkText = topMenuLinks[i].textContent.replaceAll(' ', '');
	tempMenuLinkText = tempMenuLinkText.replaceAll('\t', '');
	tempMenuLinkText = tempMenuLinkText.replaceAll('\n', '');
	if (tempMenuLinkText == titleText) {
		topMenuLinks[i].classList.add("active");
		break;
	}
}