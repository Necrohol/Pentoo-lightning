# Copyright 2024 Pentoo Project / LWIS LLC
# Distributed under the terms of the GNU General Public License v2
# Documentation and metadata: CC BY-SA 4.0

EAPI=8

inherit git-r3

DESCRIPTION="Pentoo Plymouth boot splash — Reaper Tux lightning theme with matrix rain"
HOMEPAGE="https://github.com/Necrohol/Pentoo-lightning"
EGIT_REPO_URI="https://github.com/Necrohol/Pentoo-lightning.git"
EGIT_BRANCH="master"
#archive/v${PV}.tar.gz -> ${P}.tar.gz"
EAPI=8
RESTRICT="strip"
LICENSE="GPL-2 Artistic-2 CC-BY-SA-4.0"

SLOT="0"
KEYWORDS=""
IUSE="dracut genkernel ugrd"

REQUIRED_USE="?? ( dracut genkernel ugrd )"
# Core dependencies
# sys-boot/plymouth is required to actually USE the theme.
RDEPEND="
	sys-boot/plymouth
	dracut? (
		|| (
			sys-kernel/dracut-ng
			sys-kernel/dracut
		)
	)
	ugrd? ( sys-kernel/ugrd )
	genkernel? ( sys-kernel/genkernel )
"

# BDEPEND is for the tools you use to build/fix the theme (like Pillow)
BDEPEND="
	${PYTHON_DEPS}
	$(python_gen_cond_dep '
		dev-python/pillow[${PYTHON_USEDEP}]
	')
"
src_install() {
    # Install the actual bootable theme
    insinto /usr/share/plymouth/themes/pentoo
    doins "${S}"/plymouth/pentoo/pentoo.plymouth
    doins "${S}"/plymouth/pentoo/plymouth.script
    
    # Grab the frames from your sources/preview folder
    # This keeps your repo organized but the install 'flat'
    doins "${S}"/sources/preview/frame_*.png

    # Reference Info
    dodoc "${S}"/docs/README.md
    exeinto tools
    doexe "${S}"/tools/*.py
}

# Repo layout expected:
#   plymouth/pentoo/
#     frame0001.png ... frame0120.png   (120 frames @ 24fps, 5s, 1920x1080)
#     pentoo.plymouth
#     plymouth.script

src_install() {
	insinto /usr/share/plymouth/themes/pentoo
	doins -r "${S}"/plymouth/pentoo/.
	doins "${FILESDIR}"/plymouthd.conf.example
# Docs
	dodoc -r docs/*
     dodoc License docs
insinto /usr/share/doc/${PF}
doins "${S}/LICENSE"
	# Preview symlink dir (for README consistency)
	keepdir ${theme_dir}/sources/preview

	shopt -s nullglob
	for f in "${ED}${theme_dir}"/*.png; do
		local fname=$(basename "${f}")
		dosym "../${fname}" "${theme_dir}/sources/preview/${fname}"
	done
	shopt -u nullglob
}


pkg_postinst() {
	elog ""
	elog "=== Pentoo Plymouth: Reaper Tux Lightning ==="
	elog ""
	elog "To set as default and rebuild initramfs in one step:"
	elog "  plymouth-set-default-theme -R pentoo"
	elog ""
	
	if use dracut; then
		elog "Note: dracut/dracut-ng will include this theme automatically"
		elog "on your next kernel install if 'installkernel' is configured."
	fi

	elog "Ensure 'quiet splash' is in your GRUB_CMDLINE_LINUX_DEFAULT."
	elog ""
	elog "To test without rebooting:"
	elog "  plymouthd --debug --attach-to-session; plymouth show-splash; sleep 5; plymouth quit"

	if [[ -f /proc/cmdline ]] && ! grep -q "splash" /proc/cmdline; then
		ewarn "WARNING: 'splash' missing from current boot cmdline!"
	fi
}
