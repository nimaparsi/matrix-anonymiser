import test from 'node:test';
import assert from 'node:assert/strict';
import { assemblePdfText } from '../frontend/src/lib/pdfText.ts';
const item = (str, x, y = 100, width = str.length * 5, hasEOL = false) => ({str, transform:[10,0,0,10,x,y],width,height:10,hasEOL});
test('joins split names, emails and invoice IDs without invented spaces', () => {
  assert.equal(assemblePdfText([item('john.',0),item('doe@',25),item('example.com',45)]),'john.doe@example.com');
  assert.equal(assemblePdfText([item('INV-',0),item('2026-',20),item('0318-778',45)]),'INV-2026-0318-778');
});
test('preserves word gaps, explicit whitespace and line endings', () => {
  assert.equal(assemblePdfText([item('Jane',0),item('Doe',23,100,15,true),item('Email:',0,85),item(' ',30,85),item('jane@example.com',33,85)]),'Jane Doe\nEmail: jane@example.com');
});
test('detects new baselines and large table gaps without flattening layout', () => {
  assert.equal(assemblePdfText([item('Name',0),item('Amount',100),item('Jane',0,80),item('42',100,80)]),'Name\tAmount\nJane\t42');
});
test('handles empty EOL fragments and marked-content objects', () => {
  assert.equal(assemblePdfText([item('First',0),{type:'beginMarkedContent'},item('',25,100,0,true),item('Second',0,80)]),'First\nSecond');
});
test('a trailing space must not hide a baseline change', () => {
  assert.equal(assemblePdfText([item('First ',0),item('Second',0,80)]),'First\nSecond');
});
