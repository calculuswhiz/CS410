package edu.illinois.cs.index;

public class ResultDoc {
	private int _id;
	private String _url = "[no URL]";
	private String _title = "[no title]";
	private String _content = "[no content]";
	private String _artist = "[no artist]";
	private String _lang = "[no language]";

	public ResultDoc(int id) {
		_id = id;
	}

	public int id() {
		return _id;
	}

	public String title() {
		return _title;
	}

	public ResultDoc title(String nTitle) {
		_title = nTitle;
		return this;
	}

	public ResultDoc url(String url) {
		_url = url;
		return this;
	}

	public ResultDoc artist(String artist) {
		_artist = artist;
		return this;
	}

	public ResultDoc lang(String lang) {
		_lang = lang;
		return this;
	}

	public String content() {
		return _content;
	}

	public ResultDoc content(String nContent) {
		_content = nContent;
		return this;
	}

	public String url() {
		return _url;
	}
}
