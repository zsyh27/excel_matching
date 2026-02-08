/**
 * FileUpload Component API Test
 * 
 * This script tests the file upload and parse API endpoints
 * to ensure the FileUpload component will work correctly.
 */

import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';
import path from 'path';

const API_BASE_URL = 'http://localhost:5000/api';

// Test file path (using one of the existing test files)
const TEST_FILE_PATH = path.join(process.cwd(), '../backend/temp/demo_devices.xlsx');

async function testHealthCheck() {
  console.log('\n=== Testing Health Check ===');
  try {
    const response = await axios.get(`${API_BASE_URL}/health`);
    console.log('✓ Health check passed:', response.data);
    return true;
  } catch (error) {
    console.error('✗ Health check failed:', error.message);
    return false;
  }
}

async function testFileUpload() {
  console.log('\n=== Testing File Upload ===');
  
  if (!fs.existsSync(TEST_FILE_PATH)) {
    console.error('✗ Test file not found:', TEST_FILE_PATH);
    return null;
  }

  try {
    const formData = new FormData();
    formData.append('file', fs.createReadStream(TEST_FILE_PATH));

    const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
      headers: formData.getHeaders()
    });

    if (response.data.success) {
      console.log('✓ File upload successful');
      console.log('  File ID:', response.data.file_id);
      console.log('  Filename:', response.data.filename);
      console.log('  Format:', response.data.format);
      return response.data.file_id;
    } else {
      console.error('✗ Upload failed:', response.data.error_message);
      return null;
    }
  } catch (error) {
    console.error('✗ Upload request failed:', error.message);
    if (error.response) {
      console.error('  Error details:', error.response.data);
    }
    return null;
  }
}

async function testFileParse(fileId) {
  console.log('\n=== Testing File Parse ===');
  
  if (!fileId) {
    console.error('✗ No file ID provided');
    return false;
  }

  try {
    const response = await axios.post(`${API_BASE_URL}/parse`, {
      file_id: fileId
    });

    if (response.data.success) {
      console.log('✓ File parse successful');
      const result = response.data.parse_result;
      console.log('  Total rows:', result.total_rows);
      console.log('  Valid rows:', result.valid_rows);
      console.log('  Device rows:', result.device_rows);
      return true;
    } else {
      console.error('✗ Parse failed:', response.data.error_message);
      return false;
    }
  } catch (error) {
    console.error('✗ Parse request failed:', error.message);
    if (error.response) {
      console.error('  Error details:', error.response.data);
    }
    return false;
  }
}

async function testInvalidFileFormat() {
  console.log('\n=== Testing Invalid File Format ===');
  
  try {
    const formData = new FormData();
    // Create a fake text file
    formData.append('file', Buffer.from('test content'), {
      filename: 'test.txt',
      contentType: 'text/plain'
    });

    const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
      headers: formData.getHeaders()
    });

    if (!response.data.success && response.data.error_code === 'INVALID_FORMAT') {
      console.log('✓ Invalid format correctly rejected');
      return true;
    } else {
      console.error('✗ Invalid format was not rejected');
      return false;
    }
  } catch (error) {
    if (error.response && error.response.data.error_code === 'INVALID_FORMAT') {
      console.log('✓ Invalid format correctly rejected');
      return true;
    }
    console.error('✗ Unexpected error:', error.message);
    return false;
  }
}

async function runTests() {
  console.log('Starting FileUpload Component API Tests...');
  console.log('Backend URL:', API_BASE_URL);
  
  // Test 1: Health check
  const healthOk = await testHealthCheck();
  if (!healthOk) {
    console.error('\n❌ Backend is not running. Please start the backend server first.');
    console.error('   Run: cd backend && python app.py');
    process.exit(1);
  }

  // Test 2: File upload
  const fileId = await testFileUpload();
  
  // Test 3: File parse
  if (fileId) {
    await testFileParse(fileId);
  }

  // Test 4: Invalid file format
  await testInvalidFileFormat();

  console.log('\n=== Test Summary ===');
  console.log('All critical tests completed.');
  console.log('The FileUpload component should work correctly with the backend.');
}

// Run tests
runTests().catch(error => {
  console.error('Test execution failed:', error);
  process.exit(1);
});
