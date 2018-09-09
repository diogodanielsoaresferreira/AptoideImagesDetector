try:
	from Illustration2Vector.illustration2vec_master.i2v.base import Illustration2VecBase
except:
	from i2v.base import Illustration2VecBase

caffe_available = False
chainer_available = False

try:
    from Illustration2Vector.illustration2vec_master.i2v.caffe_i2v import CaffeI2V, make_i2v_with_caffe
    caffe_available = True
except ImportError:
    pass

try:
    from Illustration2Vector.illustration2vec_master.i2v.chainer_i2v import ChainerI2V, make_i2v_with_chainer
    chainer_available = True
except ImportError:
    from i2v.chainer_i2v import ChainerI2V, make_i2v_with_chainer
    chainer_available = True

if not any([caffe_available, chainer_available]):
    raise ImportError('i2v requires caffe or chainer package')
