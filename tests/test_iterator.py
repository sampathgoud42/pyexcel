import os
import pyexcel as pe
import datetime
import copy
from base import PyexcelIteratorBase, create_sample_file2
from nose.tools import raises


class TestMatrixColumn:
    def setUp(self):
        self.data = [
            [1, 2, 3, 4, 5, 6],
            [1, 2, 3, 4],
            [1]
        ]
        self.data3 = [[1, 1], [2, 2]]
        self.result = [
            [1, 2, 3, 4, 5, 6, 1, 2],
            [1, 2, 3, 4, '', '', 1, 2],
            [1, '', '', '', '', '', '', '']
        ]

    def test_get_slice_of_columns(self):
        m = pe.iterators.Matrix(self.data)
        data = m.column[:2]
        assert data == [[1, 1, 1], [2, 2, '']]

    @raises(IndexError)
    def test_get_with_a_wrong_index(self):
        """Get with a wrong index"""
        m = pe.iterators.Matrix(self.data)
        data = m.column["hello"]  # bang, string type index 

    def test_extend_columns(self):
        """Test extend columns"""
        m = pe.iterators.Matrix(self.data)
        m.extend_columns(self.data3)
        actual = pe.utils.to_array(m)
        assert self.result == actual

    def test_iadd_list(self):
        """Test in place add a list
        """
        m2 = pe.iterators.Matrix(self.data)
        m2.column += self.data3
        actual2 = pe.utils.to_array(m2)
        assert self.result == actual2

    def test_add(self):
        """Test operator add overload
        """
        # +
        m3 = pe.iterators.Matrix(self.data)
        m4 = m3.column + self.data3
        actual3 = pe.utils.to_array(m4)
        assert self.result == actual3

    def test_iadd_matrix(self):
        """Test in place add a matrix"""
        m5 = pe.iterators.Matrix(copy.deepcopy(self.data))
        m6 = pe.iterators.Matrix(copy.deepcopy(self.data))
        m7 = m5.column + m6
        actual4 = pe.utils.to_array(m7)
        result2 = [
            [1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6],
            [1, 2, 3, 4, '','',1, 2, 3, 4,'',''],
            [1,'','','','','', 1,'','','','','']
        ]
        assert result2 == actual4

    @raises(TypeError)
    def test_type_error(self):
        m = pe.iterators.Matrix(self.data)
        m.column += 12  # bang, cannot add integers

    def test_delete_columns(self):
        r = pe.iterators.Matrix(self.data)
        # delete a list of indices
        r.delete_columns([0,2])
        assert r.row[0] == [2, 4, 5, 6]

    @raises(ValueError)
    def test_delete_wrong_type(self):
        r = pe.iterators.Matrix(self.data)
        r.delete_columns("hi")  # bang, cannot delete columns named as string

    def test_delete_one_index(self):
        m = pe.iterators.Matrix(self.data)
        del m.column[0]
        assert m.row[0] == [2, 3, 4, 5, 6]
        del m.column['A']
        assert m.row[0] == [3, 4, 5, 6]

    def test_delete_a_slice(self):
        m = pe.iterators.Matrix(self.data)
        del m.column[0:2]
        assert m.row[0] == [3, 4, 5, 6]

    def test_set_columns(self):
        r = pe.iterators.Matrix(self.data)
        content = ['r', 's', 't', 'o']
        r.column[1] = content
        assert r.column[1] == content[:3]
        assert r.column[0] == [1, 1, 1]
        r.column['B'] = ['p', 'q', 'r']
        assert r.column['B'] == ['p', 'q', 'r']

    def test_set_a_slice_of_column(self):
        r = pe.iterators.Matrix(self.data)        
        content2 = [1, 2, 3, 4]
        r.column[1:] = content2
        assert r.column[2] == content2[:3]

    def test_set_a_special_slice(self):
        r = pe.iterators.Matrix(self.data)        
        content3 = [True, False, True, False]
        r.column[0:0] = content3
        assert r.column[0] == content3[:3]

    def test_a_stepper_in_a_slice(self):
        r = pe.iterators.Matrix(self.data)        
        r.column[0:2:1] = [1, 1, 1, 1]
        assert r.column[0] == [1, 1, 1]
        assert r.column[1] == [1, 1, 1]
        assert r.column[2] == [3, 3, '']

    def test_set_an_invalid_slice(self):
        m = pe.iterators.Matrix(self.data)
        try:
            m.column[2:1] = ['e', 'r', 'r', 'o']
            assert 1 == 2
        except ValueError:
            assert 1 == 1


class TestMatrixRow:
    def setUp(self):
        self.data = [
            ['a', 'b', 'c', 'd'],
            ['e', 'f', 'g', 'h'],
            ['i', 'j', 1.1, 1]
        ]
        self.content = [['r', 's', 't', 'o'],
                        [1, 2, 3, 4],
                        [True],
                        [1.1, 2.2, 3.3, 4.4, 5.5]]

    def test_extend_rows(self):
        r = pe.iterators.Matrix(self.data)
        r.extend_rows(self.content)
        assert r.row[3] == ['r', 's', 't', 'o', '']
        assert r.row[4] == [1, 2, 3, 4, '']
        assert r.row[5] == [True, "", "", "", '']
        assert r.row[6] == [1.1, 2.2, 3.3, 4.4, 5.5]

    def test_iadd(self):
        """Test in place add"""
        r2 = pe.iterators.Matrix(self.data)
        r2.row += self.content
        assert r2.row[3] == ['r', 's', 't', 'o', '']
        assert r2.row[4] == [1, 2, 3, 4, '']
        assert r2.row[5] == [True, "", "", "", '']
        assert r2.row[6] == [1.1, 2.2, 3.3, 4.4, 5.5]

    def test_iadd_matrix(self):
        """Test in place add"""
        r2 = pe.iterators.Matrix(self.data)
        r3 = pe.iterators.Matrix(self.content)
        r2.row += r3
        assert r2.row[3] == ['r', 's', 't', 'o', '']
        assert r2.row[4] == [1, 2, 3, 4, '']
        assert r2.row[5] == [True, "", "", "", '']
        assert r2.row[6] == [1.1, 2.2, 3.3, 4.4, 5.5]

    def test_add(self):
        r3 = pe.iterators.Matrix(self.data)
        r3 = r3.row + self.content
        assert r3.row[3] == ['r', 's', 't', 'o', '']
        assert r3.row[4] == [1, 2, 3, 4, '']
        assert r3.row[5] == [True, "", "", "", '']
        assert r3.row[6] == [1.1, 2.2, 3.3, 4.4, 5.5]

    @raises(TypeError)
    def test_type_error(self):
        m = pe.iterators.Matrix(self.data)
        m.row += 12  # bang, cannot add integer
   
    def test_delete_a_index(self):
        """Delete a index"""
        r = pe.iterators.Matrix(self.data)
        content = ['i', 'j', 1.1, 1]
        assert r.row[2] == content
        del r.row[0]
        assert r.row[1] == content

    def test_delete_a_slice(self):
        """Delete a slice"""
        r2 = pe.iterators.Matrix(self.data)
        del r2.row[1:]
        assert r2.number_of_rows() == 1

    def test_delete_special_slice(self):
        r3 = pe.iterators.Matrix(self.data)
        content = ['i', 'j', 1.1, 1]        
        del r3.row[0:0]
        assert r3.row[1] == content
        assert r3.number_of_rows() == 2

    def test_delete_an_invalid_slice(self):
        m = pe.iterators.Matrix(self.data)
        try:
            del m.row[2:1]
            assert 1 == 2
        except ValueError:
            assert 1 == 1

    def test_set_a_row(self):
        r = pe.iterators.Matrix(self.data)
        content = ['r', 's', 't', 'o']
        r.row[1] = content
        assert r.row[1] == content

    def test_set_using_a_slice(self):
        """Set a list of rows"""
        r = pe.iterators.Matrix(self.data)
        content2 = [1, 2, 3, 4]
        r.row[1:] = content2
        assert r.row[2] == [1, 2, 3, 4]

    def test_a_special_slice(self):
        r = pe.iterators.Matrix(self.data)
        content3 = [True, False, True, False]
        r.row[0:0] = content3
        assert r.row[0] == [True, False, True, False]

    def test_a_stepper_in_a_slice(self):
        r = pe.iterators.Matrix(self.data)
        r.row[0:2:1] = [1, 1, 1, 1]
        assert r.row[0] == [1, 1, 1, 1]
        assert r.row[1] == [1, 1, 1, 1]
        assert r.row[2] == ['i', 'j', 1.1, 1]

    def test_a_wrong_slice(self):
        r = pe.iterators.Matrix(self.data)
        try:
            r.row[2:1] = ['e', 'r', 'r', 'o']
            assert 1 == 2
        except ValueError:
            assert 1 == 1


class TestMatrix:
    def setUp(self):
        self.data = [
            ['a', 'b', 'c', 'd'],
            ['e', 'f', 'g', 'h'],
            ['i', 'j', 1.1, 1]
        ]

    def test_empty_array_input(self):
        """Test empty array as input to Matrix"""
        m = pe.iterators.Matrix([])
        assert m.number_of_columns() == 0
        assert m.number_of_rows() == 0

    def test_update_a_cell(self):
        r = pe.iterators.Matrix(self.data)
        r[0,0] = 'k'
        assert r[0,0] == 'k'
        d = datetime.date(2014, 10, 1)
        r.cell_value(0, 1, d)
        assert isinstance(r[0,1], datetime.date) is True
        assert r[0,1].strftime("%d/%m/%y") == "01/10/14"
        r["A1"] = 'p'
        assert r[0,0] == 'p'
        r[0,1] = 16
        assert r["B1"] == 16

    def test_old_style_access(self):
        r = pe.iterators.Matrix(self.data)
        r[0,0] = 'k'
        assert r[0][0] == 'k'

    @raises(IndexError)
    def test_wrong_index_type(self):
        r = pe.iterators.Matrix(self.data)
        r["string"][0]  # bang, cannot get

    @raises(IndexError)
    def test_wrong_index_type2(self):
        r = pe.iterators.Matrix(self.data)
        r["string"] = 'k'  # bang, cannot set

    def test_transpose(self):
        """Test transpose"""
        data = [
            [1, 2, 3],
            [4, 5, 6]
        ]
        result = [
            [1, 4],
            [2, 5],
            [3, 6]
        ]
        m = pe.iterators.Matrix(data)
        m.transpose()
        actual = pe.utils.to_array(m)
        assert result == actual
                    
    def test_set_column_at(self):
        r = pe.iterators.Matrix(self.data)
        try:
            r.set_column_at(1, [11, 1], 1000)
            assert 1 == 2
        except IndexError:
            assert 1 == 1

    @raises(IndexError)
    def test_delete_rows_with_invalid_list(self):
        m = pe.iterators.Matrix([])
        m.delete_rows('ab')  # bang, cannot delete


class TestIteratableArray(PyexcelIteratorBase):
    def setUp(self):
        """
        Make a test csv file as:

        1,2,3,4
        5,6,7,8
        9,10,11,12
        """
        self.array = []
        for i in [0, 4, 8]:
            array = [i+1, i+2, i+3, i+4]
            self.array.append(array)
        self.iteratable = pe.iterators.Matrix(self.array)


class TestIterator(PyexcelIteratorBase):
    def setUp(self):
        """
        Make a test csv file as:

        1,2,3,4
        5,6,7,8
        9,10,11,12
        """
        self.testfile = "testcsv.xlsx"
        create_sample_file2(self.testfile)
        self.iteratable = pe.Reader(self.testfile)

    def tearDown(self):
        if os.path.exists(self.testfile):
            os.unlink(self.testfile)


class TestHatIterators:
    def setUp(self):
        self.testfile = "test.xlsm"
        self.content = [
            ["X", "Y", "Z"],
            [1, 2, 3],
            [1, 2, 3],
            [1, 2, 3],
            [1, 2, 3],
            [1, 2, 3]
        ]
        w = pe.Writer(self.testfile)
        w.write_array(self.content)
        w.close()

    def test_hat_column_iterator(self):
        r = pe.SeriesReader(self.testfile)
        result = pe.utils.to_dict(r)
        actual = {
            "X": [1, 1, 1, 1, 1],
            "Y": [2, 2, 2, 2, 2],
            "Z": [3, 3, 3, 3, 3],
        }
        assert result == actual

    def tearDown(self):
        if os.path.exists(self.testfile):
            os.unlink(self.testfile)

            
class TestUtilityFunctions:
    def test_excel_column_index(self):
        chars = ""
        index = pe.iterators._excel_column_index(chars)
        assert index == -1
        chars = "Z"
        index = pe.iterators._excel_column_index(chars)
        assert index == 25
        chars = "AB"
        index = pe.iterators._excel_column_index(chars)
        assert index == 27
        chars = "AAB"
        index = pe.iterators._excel_column_index(chars)
        assert index == 703

    def test_excel_cell_position(self):
        pos_chars = "A"
        row, column = pe.iterators._excel_cell_position(pos_chars)
        assert row == -1
        assert column == -1
        pos_chars = "A1"
        row, column = pe.iterators._excel_cell_position(pos_chars)
        assert row == 0
        assert column == 0
        pos_chars = "AAB111"
        row, column = pe.iterators._excel_cell_position(pos_chars)
        assert row == 110
        assert column == 703

    @raises(ValueError)
    def test_analyse_slice(self):
        a = slice(None, 3)
        bound = 4
        expected = [0, 1, 2]
        result = pe.iterators._analyse_slice(a, bound)
        assert expected == result
        a = slice(1, None)
        bound = 4
        expected = [1, 2, 3]
        result = pe.iterators._analyse_slice(a, bound)
        assert expected == result
        a = slice(2, 1)  # invalid series
        bound = 4
        result = pe.iterators._analyse_slice(a, bound) # bang
       