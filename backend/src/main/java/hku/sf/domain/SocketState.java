package hku.sf.domain;

/**
 * A socket is either working, or broken in one of two ways a person can see from
 * the desk: loose, or dead. REPAIRED and UNKNOWN exist so the history reads correctly.
 */
public enum SocketState { WORKING, LOOSE, NO_POWER, BROKEN, REPAIRED, UNKNOWN }
