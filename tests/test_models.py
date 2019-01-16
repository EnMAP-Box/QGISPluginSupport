# noinspection PyPep8Naming
import unittest, json, pickle
from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *
from qps.testing import initQgisApplication

from qps.models import *

QAPP = initQgisApplication()
SHOW_GUI = False

class ModelTests(unittest.TestCase):

    def test_treeNode(self):

        node = TreeNode(None)
        self.assertIsInstance(node, TreeNode)

        argList = list()
        kwdList = list()
        def onSignal(*args, **kwargs):
            nonlocal argList, kwdList
            argList.append(args)
            kwdList.append(kwargs)


        node.sigAddedChildren.connect(onSignal)
        n2 = TreeNode(node)
        self.assertIsInstance(n2, TreeNode)
        self.assertEqual(n2.parentNode(), node)
        QApplication.processEvents()
        self.assertTrue(len(argList) > 0)

        t = 'test'
        n2.setToolTip(t)
        assert n2.toolTip() == t

        n2.setStatusTip(t)
        assert n2.statusTip() == t



    def test_treeModel(self):

        TM = TreeModel()

        self.assertIsInstance(TM, TreeModel)

        self.assertIsInstance(TM.rootNode(), TreeNode)
        parent = TM.rootNode()

        n = 5
        nodes = []
        for i in range(n):
            n = TreeNode(parent, 'Node {}'.format(i+1))
            self.assertTrue(n.parentNode() == parent)
            nodes.append(n)


            parent = n

        for node in nodes:
            idx = TM.node2idx(node)
            self.assertIsInstance(idx, QModelIndex)
            self.assertTrue(idx.internalPointer() == node)
            self.assertTrue(TM.idx2columnName(idx), 'Node')
        self.assertTrue(TM.rowCount(None), 1)

    def test_treeView(self):

        TV = TreeView()
        self.assertIsInstance(TV, TreeView)
        TM = TreeModel()
        TV.setModel(TM)
        TV.show()

        self.assertEqual(TV.model(), TM)

        class TestNodeA(TreeNode):

            def __init__(self, *args, **kwds):
                super(TestNodeA, self).__init__(*args, **kwds)

        class TestNodeB(TreeNode):

            def __init__(self, *args, **kwds):
                super(TestNodeB, self).__init__(*args, **kwds)

            def contextMenu(self)->QMenu:
                m = QMenu()
                m2 = m.addMenu('SubMenu')
                return m

        nodes = []
        n = 5
        parent = TM.rootNode()
        for i in range(n):
            n = TreeNode(parent, name='Node {}'.format(i + 1), value=i)
            self.assertTrue(n.parentNode() == parent)
            nodes.append(n)

            idx = TM.node2idx(n)
            self.assertIsInstance(idx, QModelIndex)
            self.assertEqual(idx.isValid(), True)
            self.assertEqual(idx.internalPointer(), n)
            n2 = TM.idx2node(idx)
            self.assertEqual(n2, n)
            parent = n


        nA = TestNodeA(TM.rootNode(), name='TestNodeA')
        nB = TestNodeB(TreeNode(nA, name='SubA'), name='TestNodeB')
        nLast = TreeNode(TreeNode(nB))

        self.assertEqual(TM.findParentNode(nLast, TestNodeA), nA)
        self.assertEqual(TM.findParentNode(nLast, TestNodeB), nB)

        nB.parentNode().removeChildNode(nB)

        if SHOW_GUI:
            QAPP.exec_()

    def test_modelview(self):

        treeModel = TreeModel()
        cbModel = OptionListModel()
        for k in sorted(os.environ.keys()):
            v = os.environ[k]
            cbModel.addOption(Option(v, k, toolTip=v))

        cb = QComboBox()
        cb.setModel(cbModel)
        cb.show()

        tv = QTreeView(None)
        tv.show()
        tv.setModel(treeModel)

        rn = treeModel.rootNode()
        n1 = TreeNode(None, 'Node1')
        rn.appendChildNodes([n1])
        rn.appendChildNodes([TreeNode(rn, 'Node2')])
        n3 = TreeNode(None, 'Node3')
        n4 = TreeNode(None, 'Node4')
        n1.appendChildNodes([n3])
        n1.appendChildNodes(n4)

        print('DONE')


if __name__ == '__main__':
    SHOW_GUI = False
    unittest.main()
