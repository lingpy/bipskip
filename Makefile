training:
	@python test.py training

test-ccm1:
	@python test.py test

test-ccm2:
	@python test.py test2

test-im1:
	@python test.py test infomap

test-im2:
	@python test.py test2 infomap

test-imnex:
	@python test.py test2 infomap nex

test-ccmnex:
	@python test.py test2 nex

test-sca1:
	@python test.py sca

test-sca2:
	@python test.py sca2

test-sca1-im:
	@python test.py sca infomap

test-sca2-im:
	@python test.py sca2 infomap

test-ccm:
	@python test.py ccm
