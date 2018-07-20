/*
 * Copyright (c) 2014 CodiLime, Inc. All rights reserved.
 */

#include <vector>
#include <boost/foreach.hpp>
#include <boost/assign/list_of.hpp>

#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"

#include "bfd/rest_api/bfd_json_config.h"

namespace BFD {
namespace REST {

static bool IsIPAddressValid(const char* addr) {
    boost::system::error_code ec;
    boost::asio::ip::address::from_string(addr, ec);
    return !ec;
}

bool JsonData::ParseFromJsonString(const std::string& json) {
    tungsten_rapidjson::Document document;
    document.Parse<0>(json.c_str());
    return ParseFromJsonDocument(document);
}

void JsonData::EncodeJsonString(std::string* json) {
    tungsten_rapidjson::Document document;
    EncodeJsonDocument(&document, &document.GetAllocator());
    tungsten_rapidjson::StringBuffer strbuf;
    tungsten_rapidjson::Writer<tungsten_rapidjson::StringBuffer> writer(strbuf);
    document.Accept(writer);
    *json = strbuf.GetString();
}

bool JsonData::AreConstraintsMet(const std::vector<Constraint>& constraints,
                                const tungsten_rapidjson::Value& document) {
    if (!document.IsObject())
        return false;

    BOOST_FOREACH(const struct Constraint& constraint, constraints) {
        if (!document.HasMember(constraint.member_name) ||
            !(document[constraint.member_name].*(constraint.typecheck_func))())
            return false;
    }
    return true;
}

JsonConfig::JsonConfig()
{}

JsonConfig::JsonConfig(boost::asio::ip::address address,
                       TimeInterval desired_min_tx_interval,
                       TimeInterval required_min_rx_interval,
                       int detection_time_multiplier)
                       : address(address),
                         desired_min_tx_interval(desired_min_tx_interval),
                         required_min_rx_interval(required_min_rx_interval),
                         detection_time_multiplier(detection_time_multiplier)
                       {}

bool JsonConfig::ValidateJsonDocument(const tungsten_rapidjson::Value& document) {
    static const std::vector<Constraint> constraints = boost::assign::list_of
        (Constraint("Address", &tungsten_rapidjson::Value::IsString) )
        (Constraint("DesiredMinTxInterval", &tungsten_rapidjson::Value::IsInt))
        (Constraint("RequiredMinRxInterval", &tungsten_rapidjson::Value::IsInt))
        (Constraint("DetectionMultiplier", &tungsten_rapidjson::Value::IsInt));
    return AreConstraintsMet(constraints, document) &&
            IsIPAddressValid(document["Address"].GetString());
}

bool JsonConfig::ParseFromJsonDocument(const tungsten_rapidjson::Value& document) {
    if (ValidateJsonDocument(document)) {
        using boost::posix_time::microseconds;

        address =
            boost::asio::ip::
                address::from_string(document["Address"].GetString());
        desired_min_tx_interval =
            microseconds(document["DesiredMinTxInterval"].GetInt());
        required_min_rx_interval =
            microseconds(document["RequiredMinRxInterval"].GetInt());
        detection_time_multiplier =
            document["DetectionMultiplier"].GetInt();
        return true;
    }
    return false;
}

void JsonConfig::EncodeJsonDocument(tungsten_rapidjson::Value* document,
                                tungsten_rapidjson::Value::AllocatorType *allocator) {
    document->SetObject();
    std::string address_str = address.to_string();
    tungsten_rapidjson::Value address_val(address_str.c_str(), *allocator);
    document->AddMember("Address", address_val, *allocator);

    document->AddMember("DesiredMinTxInterval",
        desired_min_tx_interval.total_microseconds(), *allocator);
    document->AddMember("RequiredMinRxInterval",
        required_min_rx_interval.total_microseconds(), *allocator);
    document->AddMember("DetectionMultiplier",
        detection_time_multiplier, *allocator);
}

bool JsonState::ValidateJsonDocument(const tungsten_rapidjson::Value& document) {
    const std::vector<Constraint> constraints = boost::assign::list_of
        (Constraint("LocalSessionState", &tungsten_rapidjson::Value::IsString))
        (Constraint("RemoteSessionState", &tungsten_rapidjson::Value::IsString))
        (Constraint("RemoteMinRxInterval", &tungsten_rapidjson::Value::IsInt))
        (Constraint("LocalDiscriminator", &tungsten_rapidjson::Value::IsInt))
        (Constraint("RemoteDiscriminator", &tungsten_rapidjson::Value::IsInt));
    return AreConstraintsMet(constraints, document) &&
        // Check whether these strings are convertible to BFD states.
        BFDStateFromString(document["LocalSessionState"].GetString()) &&
        BFDStateFromString(document["RemoteSessionState"].GetString());
}

bool JsonState::ParseFromJsonDocument(const tungsten_rapidjson::Value& document) {
    if (!session_config.ParseFromJsonDocument(document))
        return false;

    if (ValidateJsonDocument(document)) {
        using boost::posix_time::microseconds;

        remote_min_rx_interval =
            microseconds(document["RemoteMinRxInterval"].GetInt());
        local_discriminator =
            document["LocalDiscriminator"].GetInt();
        remote_discriminator =
            document["RemoteDiscriminator"].GetInt();
        bfd_local_state =
            *BFDStateFromString(document["LocalSessionState"].GetString());
        bfd_remote_state =
            *BFDStateFromString(document["RemoteSessionState"].GetString());
        return true;
    }
    return false;
}

void JsonState::EncodeJsonDocument(tungsten_rapidjson::Value* document,
    tungsten_rapidjson::Value::AllocatorType *allocator) {
    document->SetObject();
    session_config.EncodeJsonDocument(document, allocator);

    std::string local_session_state_str
        = boost::lexical_cast<std::string>(bfd_local_state);
    tungsten_rapidjson::Value local_session_state_val(local_session_state_str.c_str(),
                                                *allocator);
    document->AddMember("LocalSessionState", local_session_state_val,
                        *allocator);

    std::string remote_session_state_str =
        boost::lexical_cast<std::string>(bfd_remote_state);
    tungsten_rapidjson::Value remote_session_state_val(remote_session_state_str.c_str(),
                                                *allocator);
    document->AddMember("RemoteSessionState", remote_session_state_val,
                        *allocator);
    document->AddMember("LocalDiscriminator", local_discriminator,
                        *allocator);
    document->AddMember("RemoteDiscriminator", remote_discriminator,
                        *allocator);
    document->AddMember("RemoteMinRxInterval",
                        remote_min_rx_interval.total_microseconds(),
                        *allocator);
}

bool JsonStateNotification::ValidateJsonDocument(
                                    const tungsten_rapidjson::Value& document) {
    const std::vector<Constraint> constraints = boost::assign::list_of
        (Constraint("Address", &tungsten_rapidjson::Value::IsString))
        (Constraint("SessionState", &tungsten_rapidjson::Value::IsString));
    return AreConstraintsMet(constraints, document) &&
            IsIPAddressValid(document["Address"].GetString()) &&
            BFDStateFromString(document["SessionState"].GetString());
}

bool JsonStateNotification::ParseFromJsonDocument(const tungsten_rapidjson::Value
                                                        &document) {
    if (ValidateJsonDocument(document)) {

        address =
            boost::asio::ip::
                address::from_string(document["Address"].GetString());
        state =
            *BFDStateFromString(document["SessionState"].GetString());
        return true;
    }
    return false;
}

void JsonStateNotification::EncodeJsonDocument(tungsten_rapidjson::Value* document,
        tungsten_rapidjson::Value::AllocatorType *allocator) {
    document->SetObject();
    std::string address_str = address.to_string();
    tungsten_rapidjson::Value address_val(address_str.c_str(), *allocator);
    document->AddMember("Address", address_val, *allocator);

    std::string session_state_str = boost::lexical_cast<std::string>(state);
    tungsten_rapidjson::Value session_state_val(session_state_str.c_str(), *allocator);
    document->AddMember("SessionState", session_state_val, *allocator);
}

void JsonStateNotificationList::EncodeJsonDocument(tungsten_rapidjson::Value* document,
        tungsten_rapidjson::Value::AllocatorType *allocator) {
    document->SetArray();
    for (std::vector<JsonStateNotification>::iterator it =
            notifications.begin(); it != notifications.end(); ++it) {
        tungsten_rapidjson::Value notification;
        it->EncodeJsonDocument(&notification, allocator);
        document->PushBack(notification, *allocator);
    }
}

bool JsonStateNotificationList::ValidateJsonDocument(
                    const tungsten_rapidjson::Value& document) {
    return true;
}

bool JsonStateNotificationList::ParseFromJsonDocument(
                    const tungsten_rapidjson::Value& document) {
    return false;
}

void JsonStateMap::EncodeJsonDocument(tungsten_rapidjson::Value* document,
    tungsten_rapidjson::Value::AllocatorType* allocator) {
    document->SetObject();

    for (StateMap::iterator it = states.begin(); it != states.end(); ++it) {
        std::string address_str = it->first.to_string();
        tungsten_rapidjson::Value address_val(address_str.c_str(), *allocator);

        std::string session_state_str =
            boost::lexical_cast<std::string>(it->second);
        tungsten_rapidjson::Value session_state_val(session_state_str.c_str(),
                                            *allocator);

        document->AddMember(address_val, session_state_val, *allocator);
    }
}

bool JsonStateMap::ValidateJsonDocument(const tungsten_rapidjson::Value& document) {
    if (!document.IsObject())
        return false;

    for (tungsten_rapidjson::Value::ConstMemberIterator it = document.MemberBegin();
            it != document.MemberEnd(); ++it) {
        using boost::system::error_code;

        if (!it->name.IsString() || !it->value.IsString())
            return false;

        error_code ec;
        if (ec != boost::system::errc::success)
            return false;
        if (!BFDStateFromString(it->value.GetString()))
            return false;
    }
    return true;
}

bool JsonStateMap::ParseFromJsonDocument(
        const tungsten_rapidjson::Value& document) {
    if (!ValidateJsonDocument(document))
        return false;

    states.clear();

    for (tungsten_rapidjson::Value::ConstMemberIterator
            it = document.MemberBegin(); it != document.MemberEnd(); ++it) {
        boost::asio::ip::address address =
            boost::asio::ip::address::from_string(it->name.GetString());
        BFDState state = *BFDStateFromString(it->value.GetString());
        states[address] = state;
    }
    return true;
}

}  // namespace REST
}  // namespace BFD

